from .spans import CHECKSUM_TYPES, Span


def _rank(span: Span) -> tuple[bool, int]:
    return (span.type in CHECKSUM_TYPES and span.source == "rules", span.end - span.start)


def _collapse(cluster: list[Span], text: str) -> Span:
    if len(set(cluster)) == 1:
        return cluster[0]
    best = max(cluster, key=_rank)
    start = min(s.start for s in cluster)
    end = max(s.end for s in cluster)
    sources = {s.source for s in cluster}
    source = best.source if len(sources) == 1 else "both"
    return Span(start, end, best.type, text[start:end], source)


def merge_spans(spans: list[Span], text: str) -> list[Span]:
    """Join overlapping spans into one so no part of either leaks."""
    merged: list[Span] = []
    cluster: list[Span] = []
    cluster_end = -1
    for span in sorted(spans, key=lambda s: (s.start, -s.end)):
        if cluster and span.start < cluster_end:
            cluster.append(span)
            cluster_end = max(cluster_end, span.end)
        else:
            if cluster:
                merged.append(_collapse(cluster, text))
            cluster, cluster_end = [span], span.end
    if cluster:
        merged.append(_collapse(cluster, text))
    return merged
