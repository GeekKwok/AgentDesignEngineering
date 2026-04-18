import requests
import json
from typing import Optional, Dict, Any


def get_repo_info(owner: str, repo: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    从 GitHub API 获取指定仓库的基本信息。

    Args:
        owner: 仓库所有者（用户名或组织名）
        repo: 仓库名称
        token: GitHub 个人访问令牌（可选，用于提高速率限制）

    Returns:
        dict: 包含仓库基本信息的字典，包含以下键：
            - name: 仓库名称
            - full_name: 仓库全名（owner/repo）
            - description: 仓库描述
            - stargazers_count: Star 数量
            - forks_count: Fork 数量
            - html_url: 仓库网页 URL
            - language: 主要编程语言
            - created_at: 创建时间
            - updated_at: 最后更新时间

    Raises:
        ImportError: 如果 requests 库未安装
        requests.exceptions.RequestException: 如果网络请求失败
        ValueError: 如果仓库不存在或 API 返回错误
    """


    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-GitHub-API-Client"
    }
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    # 提取所需字段
    result = {
        "name": data.get("name"),
        "full_name": data.get("full_name"),
        "description": data.get("description"),
        "stargazers_count": data.get("stargazers_count", 0),
        "forks_count": data.get("forks_count", 0),
        "html_url": data.get("html_url"),
        "language": data.get("language"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at")
    }
    return result


def get_repo_info_simple(owner: str, repo: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    简化版本，只返回 Star 数、Fork 数和描述。

    Args:
        owner: 仓库所有者
        repo: 仓库名称
        token: GitHub 个人访问令牌（可选）

    Returns:
        dict: 包含以下键的字典：
            - stars: Star 数量
            - forks: Fork 数量
            - description: 仓库描述
            - success: 是否成功获取

    Raises:
        同 get_repo_info
    """
    try:
        info = get_repo_info(owner, repo, token)
        return {
            "stars": info["stargazers_count"],
            "forks": info["forks_count"],
            "description": info["description"],
            "success": True
        }
    except Exception as e:
        return {
            "stars": 0,
            "forks": 0,
            "description": None,
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # 示例用法
    import sys

    if len(sys.argv) >= 3:
        owner = sys.argv[1]
        repo = sys.argv[2]
        token = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        owner = "octocat"
        repo = "Hello-World"
        token = None

    print(f"获取仓库 {owner}/{repo} 的信息...")
    try:
        info = get_repo_info_simple(owner, repo, token)
        if info["success"]:
            print(f"Stars: {info['stars']}")
            print(f"Forks: {info['forks']}")
            print(f"描述: {info['description']}")
        else:
            print(f"失败: {info.get('error')}")
    except Exception as e:
        print(f"错误: {e}")