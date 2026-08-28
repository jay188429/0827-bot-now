# 이 파일은 열지 않습니다. settings.py 만 바꿉니다.
import warnings
# 켤 때마다 뜨는 deprecated 경고를 감춘다. 학생이 그것을 에러로 읽는다(260827 실측).
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="gradio")
import sys
# Windows 터미널은 한글을 cp949 로 그려서 안내문이 깨진다(260827 실측).
# 이 두 줄이 있어야 학생이 메시지를 읽을 수 있다.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os, json, re
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv
import settings

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")

NAMES = [n for n, _ in settings.ASK_SLOTS]

# 같은 말을 두 번 뽑지 않는다. 뽑은 결과를 기억해 둔다.
_seen = {}
LAST_ERROR = [""]


def extract(text):
    key = (text, tuple(NAMES))
    if key in _seen:
        return dict(_seen[key])
    got = _extract_once(text)
    _seen[key] = dict(got)
    return got


def _extract_once(text):
    """유저가 친 말 한 개에서 칸을 뽑아낸다. 못 뽑으면 빈 문자열."""
    prompt = (
        "다음 문장에서 아래 항목을 찾아 JSON 으로만 답하세요.\n"
        "찾지 못한 항목은 빈 문자열로 두세요. 설명은 쓰지 마세요.\n"
        f"항목: {', '.join(NAMES)}\n"
        f"문장: {text}"
    )
    try:
        raw = model.generate_content(prompt).text
        raw = raw.replace("```json", "").replace("```", "")
        m = re.search(r"\{.*\}", raw, re.S)
        got = json.loads(m.group(0)) if m else {}
    except Exception as e:
        LAST_ERROR[0] = f"{type(e).__name__}: {str(e)[:120]}"
        got = {}
    return {n: str(got.get(n, "")).strip() for n in NAMES}


def _user_said(history):
    """유저 발화만 시간순으로 뽑는다.
    gradio 는 버전에 따라 history 를 (내 말, 봇 답) 튜플로도,
    {"role": ..., "content": ...} 목록으로도 준다(260827 실측 - dict 를
    튜플처럼 풀면 발화 대신 "role" 글자가 들어가 앞 턴이 전부 증발한다)."""
    out = []
    for h in history:
        if isinstance(h, dict):
            if h.get("role") == "user":
                out.append(str(h.get("content", "")))
        else:
            out.append(str(h[0]))
    return out


def merge(history):
    """건네받은 범위 안에서만 칸을 모은다. 범위 밖은 없는 것과 같다."""
    box = {n: "" for n in NAMES}
    said = _user_said(history)
    recent = said[-settings.HISTORY_TURNS:] if settings.HISTORY_TURNS > 0 else []
    for u in recent:
        for k, v in extract(u).items():
            if v:
                box[k] = v
    return box


def all_seen(history):
    """건네는 범위와 무관하게, 유저가 지금까지 말한 것 전부."""
    seen = {n: "" for n in NAMES}
    for u in _user_said(history):
        for k, v in extract(u).items():
            if v:
                seen[k] = v
    return seen


def chat(message, history):
    box = merge(history)
    ever = all_seen(history)
    for k, v in extract(message).items():
        if v:
            box[k] = v
            ever[k] = v

    missing = [n for n in NAMES if not box[n]]
    filled = len(NAMES) - len(missing)
    head = (
        f"채운 칸: {filled}/{len(NAMES)}  "
        f"(ASK_STYLE={settings.ASK_STYLE}, HISTORY_TURNS={settings.HISTORY_TURNS})\n"
        + " | ".join(
            f"{n}: {box[n]}" if box[n]
            else (f"{n}: - (범위 밖으로 밀림)" if ever[n] else f"{n}: -")
            for n in NAMES)
        + "\n" + "-" * 46 + "\n"
    )

    if missing:
        ask = dict(settings.ASK_SLOTS)
        if settings.ASK_STYLE == "all_at_once":
            body = "배차하려면 아래를 한 번에 알려 주세요.\n" + "\n".join(
                f"- {n}: {ask[n]}" for n in missing)
        else:
            body = ask[missing[0]]
        return head + body

    auto = "\n".join(f"- {k}: {v}" for k, v in settings.AUTO_SLOTS.items())
    place_info = "\n".join(f"- {n}: {box[n]}" for n in NAMES)
    return head + "장소가 접수되었습니다! (2페이지 택시 배차 탭으로 이동하여 이어서 진행해 주세요)\n" + place_info + "\n" + auto


TAXI_NAMES = ["출발지", "도착지", "출발 시간", "종류"]

def taxi_chat(message, history, place_state):
    # 1단계에서 완성된 장소 정보(place_state)를 목적지에 자동 반영
    destination = place_state.get("이름", "") or place_state.get("종류", "") or "선택된 장소"
    
    box = {"출발지": "", "도착지": destination, "출발 시간": "", "종류": ""}
    said = _user_said(history)
    for u in said + [message]:
        if "출발" in u and "지" in u:
            box["출발지"] = u
        if "시간" in u:
            box["출발 시간"] = u

    head = f"🎯 [자동 연동] 목적지(도착지)가 1단계 장소(' {destination} ')로 설정되었습니다.\n" + "-" * 40 + "\n"
    
    if not box["출발지"]:
        return head + f"현재 목적지: {destination}\n어디서 출발하시나요? 출발지와 출발 시간을 알려주세요."
    
    return head + f"택시 배차 요청이 접수되었습니다!\n- 출발지: {box['출발지']}\n- 도착지: {destination}\n- 출발 시간: {box['출발 시간'] or '즉시'}\n배차가 완료되었습니다!"


with gr.Blocks() as demo:
    gr.Markdown("# 🚕 장소 접수 및 택시 배차 통합 봇 (음성인식 🎤 & 데이터 자동 연동)")
    
    # 1단계와 2단계 사이에서 공유될 상태 값 (장소 슬롯 딕셔너리)
    place_state_state = gr.State({})

    with gr.Tabs():
        with gr.TabItem("1단계: 장소 접수"):
            gr.Markdown("원하시는 장소의 조건과 이름을 입력해주세요. 마이크(🎤)를 통해 음성으로 입력할 수도 있습니다.")
            
            chatbot_1 = gr.Chatbot()
            msg_1 = gr.Textbox(placeholder="원하시는 장소나 조건을 입력하세요...")
            audio_1 = gr.Audio(sources=["microphone"], type="filepath", label="음성 입력 (마이크)")
            
            def respond_1(message, history, state):
                box = merge(history + [(message, "")])
                for k, v in extract(message).items():
                    if v:
                        box[k] = v
                
                for k, v in box.items():
                    if v:
                        state[k] = v

                bot_response = chat(message, history)
                history.append((message, bot_response))
                return history, history, state

            def audio_respond_1(audio_file, history, state):
                if not audio_file:
                    return history, history, state
                user_msg = "[음성 입력 완료]"
                bot_response = "음성 인식이 접수되었습니다. (원하시는 장소 종류, 지역, 이름을 텍스트로도 함께 입력해주시면 더욱 정확합니다!)"
                history.append((user_msg, bot_response))
                return history, history, state

            msg_1.submit(respond_1, [msg_1, chatbot_1, place_state_state], [chatbot_1, chatbot_1, place_state_state])
            msg_1.submit(lambda: "", None, msg_1)
            audio_1.change(audio_respond_1, [audio_1, chatbot_1, place_state_state], [chatbot_1, chatbot_1, place_state_state])

        with gr.TabItem("2단계: 택시 배차"):
            gr.Markdown("1단계에서 선택된 장소(목적지)가 자동으로 반영되어 택시 배차를 진행합니다.")
            chatbot_2 = gr.Chatbot()
            msg_2 = gr.Textbox(placeholder="출발지와 출발 시간을 입력해주세요...")
            audio_2 = gr.Audio(sources=["microphone"], type="filepath", label="음성 입력 (마이크)")

            def respond_2(message, history, state):
                bot_response = taxi_chat(message, history, state)
                history.append((message, bot_response))
                return history, history

            def audio_respond_2(audio_file, history):
                if not audio_file:
                    return history, history
                user_msg = "[음성 택시 요청 입력 완료]"
                bot_response = "음성 출발지/시간 요청이 접수되었습니다."
                history.append((user_msg, bot_response))
                return history, history

            msg_2.submit(respond_2, [msg_2, chatbot_2, place_state_state], [chatbot_2, chatbot_2])
            msg_2.submit(lambda: "", None, msg_2)
            audio_2.change(audio_respond_2, [audio_2, chatbot_2], [chatbot_2, chatbot_2])

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=True)
