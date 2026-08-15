"""
Plantica Agricultural AI Assistant & Voice Service
টেক্সট, ইমেজ এবং অডিও/ভয়েস ইনপুট প্রসেস করে বাংলায় গভীর ও নির্ভুল কৃষি পরামর্শ প্রদান করে।
"""
import os
import json
import base64
import requests
from django.conf import settings

# কৃষি বিশেষজ্ঞ হিসেবে জেমিনি সিস্টেম প্রম্পট
AGRICULTURAL_SYSTEM_INSTRUCTION = """
You are 'প্ল্যান্টিকা এআই' (Plantica AI) — the most intelligent, friendly, and expert Agricultural & Gardening AI Assistant in Bangladesh.

Knowledge Base & Capabilities:
1. Rooftop & Balcony Gardening (ছাদবাগান, বারান্দা বাগান, ড্রাম ও টবে চাষাবাদ পদ্ধতি).
2. Planting Calendar for Bangladesh (কোন মাসে কোন সবজি, ফুল, ফল বা ভেষজ গাছ রোপণ করতে হবে, ৬টি ঋতুর উপযোগী ফসল).
3. Soil preparation & potting mix (দোআঁশ মাটি, বেলে মাটি, কোকোপিট, ভার্মিকম্পোস্ট অনুপাত, টবের ড্রেনেজ ব্যবস্থা).
4. Fertilizers & Plant Nutrition (ইউরিয়া, টিএসপি, ডিএপি, এমপি, বোরণ, জিংক, খৈল পচা তরল সার, হাড়ের গুঁড়ো, জৈব কম্পোস্টের সঠিক পরিমাপ ও প্রয়োগের সময়).
5. Pest, insect & disease control (জৈব বালাইনাশক, নিম তেল, ফেরোমোন ফাঁদ এবং অনুমোদিত বৈজ্ঞানিক ছত্রাকনাশক/কীটনাশক).
6. Plant Propagation (কলম করা, গুটি কলম, জোড় কলম, কাটিং ও বীজ থেকে চারা তৈরি).
7. Multimodal Image Analysis: If the user uploads a photo of a plant, leaf, soil, fruit, or garden, analyze it thoroughly and give diagnosis and specific suggestions.
8. Bengali Voice Processing: If the user provides a voice note/audio query in Bengali, understand the speech and reply with accurate agricultural solutions.

Tone & Output Style:
- Always answer in natural, polite, encouraging Bengali.
- Use clear markdown structure (bold titles, bullet points, emojis).
- Provide practical step-by-step instructions with exact measurements (e.g. "প্রতি লিটার পানিতে ২ গ্রাম", "১০ ইঞ্চি টবের জন্য ১ চা চামচ").
- At the end of the answer, always include 2-3 relevant follow-up questions under '❓ আপনার পরবর্তী জিজ্ঞাসা হতে পারে:' so the user can easily continue.
"""

CANDIDATE_GEMINI_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-1.5-flash"
]


def ask_plantica_ai_assistant(
    user_query: str = "",
    image_file=None,
    audio_file=None,
    chat_history: list = None
) -> dict:
    """
    টেক্সট, ছবি বা অডিও ইনপুট নিয়ে জেমিনি এআই থেকে বিস্তারিত উত্তর ও প্রাসঙ্গিক সাজেশন্স নিয়ে আসে।
    
    Returns:
    {
        "answer": "সম্পূর্ণ বাংলা উত্তর...",
        "spoken_summary": "ছোট সামারি (ভয়েস প্লেব্যাকের জন্য)",
        "suggested_followups": ["প্রশ্ন ১", "প্রশ্ন ২", "প্রশ্ন ৩"],
        "used_model": "gemini-3.5-flash"
    }
    """
    gemini_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY')
    if not gemini_key or not gemini_key.strip():
        raise Exception("GEMINI_API_KEY is missing in settings / .env")

    # Build parts for current turn
    current_parts = []

    # ১. যদি অডিও ভয়েস ফাইল থাকে (Voice Note / Audio Query)
    if audio_file:
        if hasattr(audio_file, 'seek'):
            audio_file.seek(0)
        if hasattr(audio_file, 'read'):
            audio_bytes = audio_file.read()
            if hasattr(audio_file, 'seek'):
                audio_file.seek(0)
        elif isinstance(audio_file, bytes):
            audio_bytes = audio_file
        else:
            with open(audio_file, 'rb') as f:
                audio_bytes = f.read()

        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Audio MIME type detection
        audio_name = getattr(audio_file, 'name', 'audio.mp3').lower()
        mime_type = 'audio/mp3'
        if audio_name.endswith('.wav'):
            mime_type = 'audio/wav'
        elif audio_name.endswith('.m4a') or audio_name.endswith('.aac'):
            mime_type = 'audio/m4a'
        elif audio_name.endswith('.ogg'):
            mime_type = 'audio/ogg'

        current_parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_audio
            }
        })

    # ২. যদি ইমেজ ফাইল থাকে (Plant / Leaf / Garden Photo)
    if image_file:
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
        if hasattr(image_file, 'read'):
            img_bytes = image_file.read()
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
        elif isinstance(image_file, bytes):
            img_bytes = image_file
        else:
            with open(image_file, 'rb') as f:
                img_bytes = f.read()

        b64_img = base64.b64encode(img_bytes).decode('utf-8')
        current_parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": b64_img
            }
        })

    # ৩. টেক্সট কুয়েরি
    text_content = user_query.strip() if user_query else ""
    if not text_content and audio_file:
        text_content = "এই অডিওতে ব্যবহারকারীর বাংলা প্রশ্ন বা বক্তব্য মনোযোগ দিয়ে শুনে তার নিখুঁত কৃষি পরামর্শ বাংলায় প্রদান করুন।"
    elif not text_content and image_file:
        text_content = "এই গাছের ছবিটি বিশ্লেষণ করে এর প্রজাতি, স্বাস্থ্যগত অবস্থা ও সঠিক পরিচর্যার পরামর্শ বাংলায় প্রদান করুন।"

    if text_content:
        current_parts.append({"text": text_content})

    if not current_parts:
        raise ValueError("কমপক্ষে টেক্সট, ছবি বা ভয়েস মেসেজ পাঠানো আবশ্যক।")

    # Construct complete conversation contents
    contents = []

    # Append previous history if exists
    if chat_history and isinstance(chat_history, list):
        for msg in chat_history:
            role = "user" if msg.get("role") in ["user", "human"] else "model"
            msg_text = msg.get("text", "")
            if msg_text:
                contents.append({
                    "role": role,
                    "parts": [{"text": msg_text}]
                })

    # Append current user prompt
    contents.append({
        "role": "user",
        "parts": current_parts
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": AGRICULTURAL_SYSTEM_INSTRUCTION}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048
        }
    }

    # Call Gemini with fallback models
    last_error = None
    for model_name in CANDIDATE_GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
        try:
            r = requests.post(url, json=payload, timeout=12)
            if r.status_code == 200:
                res_data = r.json()
                answer_text = res_data['candidates'][0]['content']['parts'][0]['text'].strip()

                # Extract suggested follow-ups
                followups = []
                if "❓" in answer_text:
                    parts = answer_text.split("❓", 1)
                    if len(parts) > 1:
                        f_lines = parts[1].split("\n")
                        for l in f_lines:
                            clean_l = l.strip(" *123456789০১২৩৪৫৬৭৮৯.-_?❓")
                            if clean_l and len(clean_l) > 6:
                                followups.append(clean_l)

                if not followups:
                    followups = [
                        "টবে সার দেওয়ার সঠিক নিয়ম কী?",
                        "গাছের পাতা হলুদ হওয়া বন্ধ করার উপায় কী?",
                        "বর্ষায় ছাদবাগানের বিশেষ যত্ন কীভাবে নেব?"
                    ]

                # Short spoken summary (first 1-2 sentences for Voice Assistant playback)
                first_paragraph = answer_text.split('\n\n')[0].replace('#', '').replace('*', '').strip()
                if len(first_paragraph) > 200:
                    first_paragraph = first_paragraph[:200] + "..."

                return {
                    "answer": answer_text,
                    "spoken_summary": first_paragraph,
                    "suggested_followups": followups[:3],
                    "used_model": model_name
                }
            else:
                last_error = f"{model_name} (Status {r.status_code}): {r.text[:120]}"
        except Exception as conn_err:
            last_error = f"{model_name}: {conn_err}"

    raise Exception(f"Gemini API Error: {last_error}")
