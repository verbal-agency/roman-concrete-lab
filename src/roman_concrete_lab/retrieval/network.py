"""Read-only exact-host network adapter for owner-activated G10R runs."""

from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from jsonschema import validate

from .contracts import (
    InvestigationBudget,
    PolicyBlocked,
    SourcePolicy,
    digest,
    normalize_query,
)
from .pdf import DocumentExtractionError, extract_pdf


class NetworkUnavailable(RuntimeError):
    """The configured read-only transport did not return a usable response."""


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._ignored = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignored += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            attributes = {key.lower(): value for key, value in attrs if value is not None}
            name = (attributes.get("name") or attributes.get("property") or "").lower()
            if name in {
                "description",
                "og:description",
                "citation_title",
                "citation_abstract",
                "dc.title",
                "dc.description",
            } and attributes.get("content"):
                self.parts.append(attributes["content"].strip())

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored:
            self._ignored -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if not self._ignored and self._in_title and data.strip():
            self.parts.append(data.strip())

    def text(self) -> str:
        return "\n".join(self.parts)


Transport = Callable[[str, int, str], tuple[str, str, bytes]]


class _PolicyRedirectHandler(HTTPRedirectHandler):
    def __init__(self, policy: SourcePolicy, fetch_content: bool) -> None:
        super().__init__()
        self.policy = policy
        self.fetch_content = fetch_content

    def redirect_request(
        self,
        req: Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> Request | None:
        self.policy.decide(newurl, fetch_content=self.fetch_content)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class ConfiguredNetworkRetrievalAdapter:
    """Searches frozen scholarly indexes and fetches exact allowed public pages."""

    def __init__(
        self,
        *,
        policy: SourcePolicy,
        budget: InvestigationBudget,
        source_schema: dict[str, Any],
        transport: Transport | None = None,
        timeout_seconds: int = 20,
        user_agent: str = "roman-concrete-lab-g10r/1.0 (read-only research pilot)",
    ) -> None:
        self.policy = policy
        self.budget = budget
        self.source_schema = source_schema
        self.transport = transport
        self.timeout_seconds = timeout_seconds
        self.user_agent = user_agent
        self._query_cache: dict[str, list[dict[str, Any]]] = {}
        self._seen_dedup: set[str] = set()

    def _urllib_transport(
        self,
        url: str,
        timeout: int,
        user_agent: str,
        *,
        fetch_content: bool,
    ) -> tuple[str, str, bytes]:
        request = Request(url, headers={"User-Agent": user_agent, "Accept": "application/pdf,text/html;q=0.9,application/json;q=0.8,*/*;q=0.1"}, method="GET")
        try:
            opener = build_opener(_PolicyRedirectHandler(self.policy, fetch_content))
            with opener.open(request, timeout=timeout) as response:
                limit = int(self.policy.record["request_policy"]["max_response_bytes"])
                payload = response.read(limit + 1)
                if len(payload) > limit:
                    raise PolicyBlocked("response exceeds frozen payload limit")
                return response.geturl(), response.headers.get_content_type(), payload
        except PolicyBlocked:
            raise
        except Exception as exc:
            raise NetworkUnavailable(f"GET failed for configured host: {type(exc).__name__}: {exc}") from exc

    def _get(self, url: str, *, fetch_content: bool) -> tuple[str, str, bytes]:
        self.policy.decide(url, fetch_content=fetch_content)
        if self.transport is None:
            final_url, content_type, payload = self._urllib_transport(
                url,
                self.timeout_seconds,
                self.user_agent,
                fetch_content=fetch_content,
            )
        else:
            final_url, content_type, payload = self.transport(
                url, self.timeout_seconds, self.user_agent
            )
        self.policy.decide(final_url, fetch_content=fetch_content)
        return final_url, content_type, payload

    def search(
        self,
        query: str,
        *,
        index: str,
        problem_id: str,
        problem_version: str,
    ) -> dict[str, Any]:
        normalized = normalize_query(query)
        if index not in {"openalex", "crossref"}:
            raise PolicyBlocked(f"search index is not configured: {index}")
        cache_key = f"{index}:{normalized}"
        if cache_key in self._query_cache:
            return {"query": normalized, "index": index, "replayed": True, "results": self._query_cache[cache_key]}
        self.budget.debit(queries=1)
        if index == "openalex":
            url = "https://api.openalex.org/works?" + urlencode({"search": normalized, "per-page": 5})
        else:
            url = "https://api.crossref.org/works?" + urlencode({"query.bibliographic": normalized, "rows": 5})
        _, _, payload = self._get(url, fetch_content=False)
        try:
            document = json.loads(payload)
        except Exception as exc:
            raise NetworkUnavailable(f"malformed {index} response: {exc}") from exc
        candidates = self._parse_openalex(document, normalized, problem_id, problem_version) if index == "openalex" else self._parse_crossref(document, normalized, problem_id, problem_version)
        retained = []
        for candidate in candidates:
            if candidate["deduplication_key"] in self._seen_dedup:
                candidate["status"] = "DUPLICATE"
            else:
                self.budget.debit(retained_sources=1)
                self._seen_dedup.add(candidate["deduplication_key"])
            validate(candidate, self.source_schema)
            retained.append(candidate)
        self._query_cache[cache_key] = retained
        return {"query": normalized, "index": index, "replayed": False, "results": retained}

    def _parse_openalex(
        self,
        document: dict[str, Any],
        query: str,
        problem_id: str,
        problem_version: str,
    ) -> list[dict[str, Any]]:
        candidates = []
        for item in document.get("results", []):
            work_id = str(item.get("id", "")).rsplit("/", 1)[-1]
            if not work_id or not item.get("title"):
                continue
            doi = str(item.get("doi") or "").removeprefix("https://doi.org/").lower()
            locator = f"https://api.openalex.org/works/{quote(work_id)}"
            landing = (item.get("primary_location") or {}).get("landing_page_url")
            candidates.append(
                self._candidate(
                    source_id=f"OA-{work_id}",
                    title=item["title"],
                    locator=locator,
                    query=query,
                    problem_id=problem_id,
                    problem_version=problem_version,
                    deduplication_key=f"doi:{doi}" if doi else f"openalex:{work_id.lower()}",
                    host="api.openalex.org",
                    content_locator=self._permitted_public_locator(landing),
                )
            )
        return candidates

    def _parse_crossref(
        self,
        document: dict[str, Any],
        query: str,
        problem_id: str,
        problem_version: str,
    ) -> list[dict[str, Any]]:
        candidates = []
        for item in document.get("message", {}).get("items", []):
            titles = item.get("title") or []
            doi = str(item.get("DOI") or "").lower()
            if not titles or not doi:
                continue
            candidates.append(
                self._candidate(
                    source_id="CR-" + digest(doi)[7:19],
                    title=titles[0],
                    locator=f"https://doi.org/{quote(doi, safe='/()')}",
                    query=query,
                    problem_id=problem_id,
                    problem_version=problem_version,
                    deduplication_key=f"doi:{doi}",
                    host="doi.org",
                    content_locator=None,
                )
            )
        return candidates

    def _permitted_public_locator(self, locator: Any) -> str | None:
        if not isinstance(locator, str) or not locator.startswith("https://"):
            return None
        try:
            self.policy.decide(locator, fetch_content=True)
        except PolicyBlocked:
            return None
        return locator

    @staticmethod
    def _candidate(
        *,
        source_id: str,
        title: str,
        locator: str,
        query: str,
        problem_id: str,
        problem_version: str,
        deduplication_key: str,
        host: str,
        content_locator: str | None,
    ) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "source_candidate_id": source_id,
            "problem_id": problem_id,
            "problem_version": problem_version,
            "title": title,
            "locator": locator,
            "content_locator": content_locator,
            "discovery_query": query,
            "host": host,
            "access_class": "METADATA_ONLY",
            "rights_state": "METADATA_ONLY",
            "content_hash": None,
            "deduplication_key": deduplication_key,
            "support_region": "unadjudicated scholarly metadata",
            "contradiction_ids": [],
            "status": "DISCOVERED",
        }

    def fetch_public_text(self, locator: str) -> dict[str, Any]:
        response = self.fetch_public_payload(locator)
        final_url = response["locator"]
        content_type = response["content_type"]
        payload = response["payload"]

        policy = self.policy.record["request_policy"]
        if content_type == "application/pdf":
            try:
                return {
                    "locator": final_url,
                    "payload_bytes": len(payload),
                    **extract_pdf(
                        payload,
                        locator=final_url,
                        max_pages=int(policy["max_pdf_pages"]),
                        max_characters=int(policy["max_extracted_characters"]),
                    ),
                }
            except DocumentExtractionError as exc:
                raise PolicyBlocked(str(exc)) from exc
        if content_type in {"text/html", "application/xhtml+xml"}:
            parser = _TextExtractor()
            parser.feed(payload.decode("utf-8", errors="replace"))
            text = parser.text()
        else:
            raise PolicyBlocked(
                f"content type requires an undeclared metadata extractor: {content_type}"
            )
        return {
            "locator": final_url,
            "content_type": content_type,
            "text": text[:12_000],
            "payload_bytes": len(payload),
            "content_hash": "sha256:" + hashlib.sha256(payload).hexdigest(),
            "parser": "html-metadata-1.0",
            "page_count": 1,
            "extraction_status": "PARTIAL",
            "pages": [{
                "page_number": 1,
                "locator": f"{final_url}#page=1",
                "text": text[:12_000],
                "text_hash": "sha256:" + hashlib.sha256(text[:12_000].encode("utf-8")).hexdigest(),
                "text_characters": len(text[:12_000]),
                "status": "PARTIAL",
            }],
        }

    def fetch_public_payload(self, locator: str) -> dict[str, Any]:
        """Return a permitted payload to a caller that owns an ignored raw cache."""
        final_url, content_type, payload = self._get(locator, fetch_content=True)
        self.budget.debit(payload_bytes=len(payload))
        return {
            "locator": final_url,
            "content_type": content_type,
            "payload_bytes": len(payload),
            "payload": payload,
        }
