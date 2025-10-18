#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지식 그래프(JSON)를 브라우저에서 인터랙티브하게 시각화(서버 없이)하는 스크립트
 - 입력: demon_slayer_knowledge_graph.json (또는 임의 JSON)
 - 출력: knowledge_graph.html (pyvis로 생성, 로컬 브라우저에서 열기 가능)
"""

import json
import ast
import argparse
import webbrowser
import traceback
import os
from pathlib import Path
from typing import Dict, Any, List
try:
    # Python 3.8+
    from importlib import metadata as importlib_metadata
except Exception:  # pragma: no cover
    import importlib_metadata  # type: ignore

try:
    from pyvis.network import Network  # 선택적: 현재는 사용하지 않음
except Exception:
    Network = None  # pyvis 문제가 있더라도 동작하도록


def _parse_json_text(text: str) -> Dict[str, Any]:
    """느슨한 입력도 최대한 파싱하도록 방어적으로 처리.
    - UTF-8 BOM 제거
    - 코드펜스(``` 또는 ```json) 제거
    - 앞/뒤 불필요한 문자열 잘라내고 첫 '{'부터 마지막 '}'까지만 파싱
    - 최후 수단: ast.literal_eval로 파이썬 dict 스타일을 JSON으로 간주
    """
    cleaned = text.lstrip('\ufeff').strip()

    # 코드펜스 제거
    if cleaned.startswith("```"):
        first_nl = cleaned.find('\n')
        if first_nl != -1:
            cleaned = cleaned[first_nl + 1 :]
        if cleaned.endswith("```"):
            cleaned = cleaned[: cleaned.rfind("```")]
        cleaned = cleaned.strip()

    # JSON 본문 구간만 추출
    if cleaned and cleaned[0] != '{':
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            cleaned = cleaned[start : end + 1]

    # 1차 시도: 표준 JSON
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2차 시도: 파이썬 dict 리터럴을 JSON으로 간주
    try:
        obj = ast.literal_eval(cleaned)
        if isinstance(obj, dict):
            return obj  # 타입은 JSON 직렬화 가능한 기본형만 사용되었다고 가정
    except Exception:
        pass

    # 실패시 원문을 힌트로 포함한 예외
    raise ValueError("JSON 파싱 실패. 파일 형식이 손상되었을 수 있습니다.")


def load_knowledge_graph(json_path: Path, debug: bool = False) -> Dict[str, Any]:
    # 0) 먼저 정석적인 json.load 시도 (가장 안전)
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e0:
        if debug:
            print(f"[debug] json.load 실패: {e0}")

    # 1) 텍스트 기반 로드 후 방어적 파싱
    with open(json_path, 'r', encoding='utf-8') as f:
        text = f.read()
    if debug:
        preview = text[:200].replace('\n', ' ')
        ords = ' '.join(str(ord(c)) for c in text[:12])
        print(f"[debug] 입력 파일: {json_path.resolve()} | 길이: {len(text)} | 미리보기: {preview}")
        print(f"[debug] 선두 코드포인트: {ords}")
    return _parse_json_text(text)


def build_tooltip(description: str, attributes: Dict[str, Any]) -> str:
    parts: List[str] = []
    if description:
        parts.append(description)
    if attributes:
        attr_lines = [f"{k}: {v}" for k, v in attributes.items()]
        parts.append("<br/>".join(attr_lines))
    return "<br/>".join(parts)


def visualize_knowledge_graph(data: Dict[str, Any], output_html: Path, open_browser: bool = False) -> None:
    # 엔티티 노드 색상 매핑
    color_by_type = {
        "인물": "#f97316",   # orange
        "장소": "#3b82f6",   # blue
        "사물": "#22c55e",   # green
        "개념": "#a855f7",   # purple
        "기타": "#64748b"    # slate
    }

    # 1) pyvis로 먼저 시도 (브라우저 자동 오픈 없이 파일만 저장)
    try:
        if Network is None:
            raise RuntimeError("pyvis가 설치되지 않았습니다")

        net = Network(height="800px", width="100%", directed=True, bgcolor="#ffffff", font_color="#222")
        # 물리 옵션 (JSON 문자열로 전달)
        import json as _json
        options = {
            "nodes": {"shape": "dot", "size": 18},
            "edges": {"arrows": {"to": {"enabled": True, "scaleFactor": 0.7}}, "smooth": {"type": "dynamic"}},
            "physics": {"stabilization": {"iterations": 250}}
        }
        net.set_options(_json.dumps(options))

        # 엔티티 노드
        entities = {e.get("id", e.get("name")): e for e in data.get("entities", [])}
        for entity_id, entity in entities.items():
            entity_name = entity.get("name", entity_id)
            entity_type = entity.get("type", "기타")
            description = entity.get("description", "")
            attributes = entity.get("attributes", {}) or {}
            title_html = build_tooltip(description, attributes) or entity_name
            net.add_node(n_id=entity_id, label=entity_name, color=color_by_type.get(entity_type, color_by_type["기타"]), title=title_html, shape="dot")

        # 관계 엣지
        for rel in data.get("relationships", []) or []:
            src = rel.get("source")
            dst = rel.get("target")
            if not src or not dst:
                continue
            net.add_edge(src, dst, label=rel.get("relationship", ""), title=rel.get("description", ""))

        # 사건 노드 및 연결
        for event in data.get("events", []) or []:
            event_id_raw = event.get("id") or event.get("name")
            if not event_id_raw:
                continue
            event_id = f"event:{event_id_raw}"
            event_name = event.get("name", event_id_raw)
            event_desc = event.get("description", "")
            seq = event.get("sequence")
            title_lines = [event_desc]
            if seq is not None:
                title_lines.append(f"순서: {seq}")
            net.add_node(n_id=event_id, label=event_name, color="#111827", title="<br/>".join([t for t in title_lines if t]), shape="diamond")

            for participant in event.get("participants", []) or []:
                if participant in entities:
                    net.add_edge(event_id, participant, label="참여", title="참여")
            loc = event.get("location")
            if loc and loc in entities:
                net.add_edge(event_id, loc, label="장소", title="장소")

        # 파일만 저장 (브라우저 자동 오픈 방지)
        if hasattr(net, "write_html"):
            net.write_html(str(output_html), open_browser=False)
            try:
                print(f"[success] pyvis 렌더링 완료: {output_html.resolve()}")
            except Exception:
                print("[success] pyvis 렌더링 완료")
        else:
            # 구버전 호환: show()는 브라우저를 열 수 있으므로 예외 처리
            net.show(str(output_html))
            try:
                print(f"[success] pyvis 렌더링 완료: {output_html.resolve()}")
            except Exception:
                print("[success] pyvis 렌더링 완료")

    except Exception as e:
        # pyvis 렌더링 실패 시 상세 진단 정보 출력 후 종료 (폴백 없음)
        _print_pyvis_diagnostics(e, data, output_html)
        raise RuntimeError(f"pyvis 렌더링 실패: {e}")

    if open_browser:
        _open_html_in_browser(output_html)


def _write_custom_html(data: Dict[str, Any], output_html: Path) -> None:
    # 색상 매핑은 pyvis 버전과 동일하게 유지
    color_by_type = {
        "인물": "#f97316",
        "장소": "#3b82f6",
        "사물": "#22c55e",
        "개념": "#a855f7",
        "기타": "#64748b"
    }

    # 노드/엣지 배열 구성
    entities = {e.get("id", e.get("name")): e for e in data.get("entities", [])}
    nodes = []
    for entity_id, entity in entities.items():
        nodes.append({
            "id": entity_id,
            "label": entity.get("name", entity_id),
            "color": color_by_type.get(entity.get("type", "기타"), color_by_type["기타"]),
            "shape": "dot",
            "title": (entity.get("description") or "")
        })

    # 사건 노드
    for event in data.get("events", []) or []:
        event_id_raw = event.get("id") or event.get("name")
        if not event_id_raw:
            continue
        event_id = f"event:{event_id_raw}"
        title_lines = [event.get("description") or ""]
        if event.get("sequence") is not None:
            title_lines.append(f"순서: {event['sequence']}")
        nodes.append({
            "id": event_id,
            "label": event.get("name", event_id_raw),
            "color": "#111827",
            "shape": "diamond",
            "title": "<br/>".join([t for t in title_lines if t])
        })

    edges = []
    for rel in data.get("relationships", []) or []:
        if rel.get("source") and rel.get("target"):
            edges.append({
                "from": rel["source"],
                "to": rel["target"],
                "label": rel.get("relationship", ""),
                "title": rel.get("description", "")
            })

    for event in data.get("events", []) or []:
        event_id_raw = event.get("id") or event.get("name")
        if not event_id_raw:
            continue
        event_id = f"event:{event_id_raw}"
        for participant in event.get("participants", []) or []:
            if participant in entities:
                edges.append({"from": event_id, "to": participant, "label": "참여", "title": "참여"})
        loc = event.get("location")
        if loc and loc in entities:
            edges.append({"from": event_id, "to": loc, "label": "장소", "title": "장소"})

    # 순수 HTML (vis-network CDN 사용)
    import json as _json
    html = f"""
<!doctype html>
<html lang=ko>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Knowledge Graph</title>
  <style>
    html, body {{ height: 100%; margin: 0; }}
    #mynetwork {{ width: 100%; height: 100vh; border: 1px solid #e5e7eb; }}
  </style>
  <script src="https://unpkg.com/vis-network@9.1.2/dist/vis-network.min.js"></script>
  <link href="https://unpkg.com/vis-network@9.1.2/styles/vis-network.min.css" rel="stylesheet" />
  <script>
    const nodes = new vis.DataSet({_json.dumps(nodes)});
    const edges = new vis.DataSet({_json.dumps(edges)});
    window.addEventListener('DOMContentLoaded', () => {{
      const container = document.getElementById('mynetwork');
      const data = {{ nodes, edges }};
      const options = {{
        nodes: {{ shape: 'dot', size: 18 }},
        edges: {{ arrows: {{ to: {{ enabled: true, scaleFactor: 0.7 }} }}, smooth: {{ type: 'dynamic' }} }},
        physics: {{ stabilization: {{ iterations: 250 }} }}
      }};
      new vis.Network(container, data, options);
    }});
  </script>
  </head>
<body>
  <div id="mynetwork"></div>
</body>
</html>
"""
    output_html.write_text(html, encoding="utf-8")


def _open_html_in_browser(output_html: Path) -> None:
    # 기본 시도
    try:
        webbrowser.open(output_html.resolve().as_uri())
        return
    except Exception:
        pass

    # WSL / 리눅스 대체 시도
    import subprocess, shutil, os
    uri = str(output_html.resolve())
    # wslview 우선
    if shutil.which('wslview'):
        try:
            subprocess.run(['wslview', uri], check=False)
            return
        except Exception:
            pass
    # xdg-open
    if shutil.which('xdg-open'):
        try:
            subprocess.run(['xdg-open', uri], check=False)
            return
        except Exception:
            pass
    # Windows (WSL) 우회
    if shutil.which('cmd.exe'):
        try:
            win_path = subprocess.check_output(['wslpath', '-w', uri]).decode().strip()
            subprocess.run(['cmd.exe', '/c', 'start', win_path], check=False)
            return
        except Exception:
            pass


def _version_or_missing(pkg_name: str) -> str:
    try:
        return importlib_metadata.version(pkg_name)
    except Exception:
        return "미설치/확인불가"


def _print_pyvis_diagnostics(exc: Exception, data: Dict[str, Any], output_html: Path) -> None:
    # 예외와 환경을 상세 출력
    print("[diagnostics] 예외 타입:", type(exc).__name__)
    print("[diagnostics] 예외 메시지:", repr(str(exc)))
    print("[diagnostics] 스택트레이스:\n" + traceback.format_exc())

    print("[diagnostics] 출력 파일:", output_html.resolve())
    try:
        parent = output_html.resolve().parent
        can_write = parent.exists() and parent.is_dir() and os.access(str(parent), os.W_OK)
    except Exception:
        can_write = False
    print("[diagnostics] 출력 디렉토리 쓰기 가능:", can_write)

    # 버전 정보
    print("[diagnostics] pyvis 버전:", _version_or_missing("pyvis"))
    print("[diagnostics] Jinja2 버전:", _version_or_missing("Jinja2"))
    print("[diagnostics] networkx 버전:", _version_or_missing("networkx"))

    # Jinja2 임포트 확인
    try:
        import jinja2  # type: ignore
        print("[diagnostics] Jinja2 임포트 OK:", getattr(jinja2, "__version__", "unknown"))
    except Exception as je:  # pragma: no cover
        print("[diagnostics] Jinja2 임포트 실패:", repr(je))

    # 그래프 요약
    try:
        num_entities = len(data.get("entities", []))
        num_rels = len(data.get("relationships", []))
        num_events = len(data.get("events", []))
        print(f"[diagnostics] 그래프 요약: entities={num_entities}, relationships={num_rels}, events={num_events}")
    except Exception:
        pass


def parse_args() -> argparse.Namespace:
    # 파라미터 비활성: 상수로 고정 실행. 필요 시 하단 상수 변경.
    class _Args:
        input = "demon_slayer_knowledge_graph.json"
        output = "knowledge_graph.html"
        no_open = True
        open = False
        debug = False
    return _Args()


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="지식 그래프 JSON을 HTML로 시각화합니다.")
    parser.add_argument(
        "input_file", 
        nargs='?', 
        default="demon_slayer_knowledge_graph.json",
        help="입력 JSON 파일 경로 (기본값: demon_slayer_knowledge_graph.json)"
    )
    parser.add_argument(
        "output_file",
        nargs='?',
        default="knowledge_graph.html",
        help="출력 HTML 파일 경로 (기본값: knowledge_graph.html)"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="작업 완료 후 HTML 파일을 브라우저에서 엽니다."
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="HTML 파일을 브라우저에서 열지 않습니다."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="디버그 모드로 실행하여 추가 정보를 출력합니다."
    )

    args = parser.parse_args()

    # 입력 파일 경로를 스크립트 파일 기준으로 설정
    script_dir = Path(__file__).parent
    input_path = script_dir / args.input_file
    output_path = script_dir / args.output_file

    if not input_path.is_file():
        print(f"입력 파일을 찾을 수 없습니다: {input_path.resolve()}")
        return 1

    try:
        # 1. 지식 그래프 데이터 로드
        print(f"지식 그래프 로딩 중: {input_path.resolve()}")
        kg_data = load_knowledge_graph(input_path, debug=args.debug)
        
        # 2. Pyvis 네트워크 생성
        net = Network(height="800px", width="100%", directed=True, bgcolor="#ffffff", font_color="#222")
        
        # 3. HTML 생성
        print(f"HTML 파일 생성 중: {output_path.resolve()}")
        visualize_knowledge_graph(kg_data, output_path, open_browser=not args.no_open and args.open)
        
        print("\n=== 시각화 완료 ===")
        print(f"HTML 파일이 생성되었습니다: {output_path.resolve()}")
        
        if not args.no_open and args.open:
            print("브라우저에서 결과물을 엽니다.")
        else:
            print("생성된 HTML 파일을 직접 열어 확인하세요.")
            
    except Exception as e:
        print(f"시각화 중 오류 발생: {e}")
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


