import os
import json
import requests

API_KEY = os.environ.get("SERPAPI_KEY", "").strip()
AUTHOR_ID = "Mfp83rUAAAAJ"
NUM_PER_PAGE = 40


def fetch_page(start):
    url = (
        "https://serpapi.com/search.json"
        f"?engine=google_scholar_author"
        f"&author_id={AUTHOR_ID}"
        f"&hl=en"
        f"&api_key={API_KEY}"
        f"&start={start}"
        f"&num={NUM_PER_PAGE}"
    )

    print(f"正在请求: start={start}, num={NUM_PER_PAGE}")
    response = requests.get(url, timeout=30)
    print(f"HTTP 状态码: {response.status_code}")

    response.raise_for_status()

    try:
        data = response.json()
    except Exception as e:
        raise RuntimeError(f"返回内容不是合法 JSON: {e}\n原始前500字符:\n{response.text[:500]}")

    if "error" in data:
        raise RuntimeError(f"SerpApi 返回 error: {data['error']}")

    return data


def parse_stats(data):
    stats = {"total_citations": 0, "h_index": 0}

    cited_by = data.get("cited_by", {})
    table = cited_by.get("table", [])

    for row in table:
        if "citations" in row:
            stats["total_citations"] = row["citations"].get("all", 0)
        elif "h_index" in row:
            stats["h_index"] = row["h_index"].get("all", 0)

    return stats


def main():
    print(f"开始抓取，AUTHOR_ID = {AUTHOR_ID}")

    if not API_KEY:
        raise RuntimeError("未找到 SERPAPI_KEY，请检查环境变量或 GitHub Secrets。")

    citations_data = []
    author_stats = {"total_citations": 0, "h_index": 0}

    try:
        for page_idx, start in enumerate([0, 40], start=1):
            data = fetch_page(start)

            if page_idx == 1:
                author_stats = parse_stats(data)
                print(
                    f"抓到作者统计：total_citations={author_stats['total_citations']}, "
                    f"h_index={author_stats['h_index']}"
                )

            articles = data.get("articles", None)
            if articles is None:
                raise RuntimeError(
                    f"返回中没有 articles 字段。实际 keys: {list(data.keys())}"
                )

            print(f"第 {page_idx} 页抓到 {len(articles)} 篇")

            for article in articles:
                title = article.get("title", "").strip()
                cited_by = article.get("cited_by", {})
                citations = cited_by.get("value", 0)

                if title:
                    citations_data.append({
                        "title": title,
                        "citations": citations
                    })

            # 如果这一页数量小于请求页大小，说明到最后一页了
            if len(articles) < NUM_PER_PAGE:
                print("已经到最后一页，停止翻页。")
                break

    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        print("⚠️ 为避免把旧数据覆盖成全零，本次不写入 citations.json")
        return

    # 去重
    unique_data = {}
    for item in citations_data:
        title = item["title"]
        citations = item["citations"]
        if title not in unique_data or citations > unique_data[title]:
            unique_data[title] = citations

    final_articles = [
        {"title": title, "citations": citations}
        for title, citations in unique_data.items()
    ]

    # 安全保护：如果结果为空，不覆盖旧文件
    if not final_articles:
        print("⚠️ 没抓到任何文章数据，停止写入，保留旧 citations.json")
        return

    output_json = {
        "stats": author_stats,
        "articles": final_articles
    }

    with open("citations.json", "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=2)

    print(f"✅ 已保存 citations.json，共 {len(final_articles)} 篇文章")


if __name__ == "__main__":
    main()
