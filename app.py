from flask import Flask, render_template, request, jsonify
import requests
import random
from datetime import datetime, date, timedelta
import json
import os

app = Flask(__name__)

# Знаки зодиака
ZODIAC_SIGNS = {
    'aries': {'ja': '牡羊座 (おひつじ座)', 'en': 'Aries', 'emoji': '♈'},
    'taurus': {'ja': '牡牛座 (おうし座)', 'en': 'Taurus', 'emoji': '♉'},
    'gemini': {'ja': '双子座 (ふたご座)', 'en': 'Gemini', 'emoji': '♊'},
    'cancer': {'ja': '蟹座 (かに座)', 'en': 'Cancer', 'emoji': '♋'},
    'leo': {'ja': '獅子座 (しし座)', 'en': 'Leo', 'emoji': '♌'},
    'virgo': {'ja': '乙女座 (おとめ座)', 'en': 'Virgo', 'emoji': '♍'},
    'libra': {'ja': '天秤座 (てんびん座)', 'en': 'Libra', 'emoji': '♎'},
    'scorpio': {'ja': '蠍座 (さそり座)', 'en': 'Scorpio', 'emoji': '♏'},
    'sagittarius': {'ja': '射手座 (いて座)', 'en': 'Sagittarius', 'emoji': '♐'},
    'capricorn': {'ja': '山羊座 (やぎ座)', 'en': 'Capricorn', 'emoji': '♑'},
    'aquarius': {'ja': '水瓶座 (みずがめ座)', 'en': 'Aquarius', 'emoji': '♒'},
    'pisces': {'ja': '魚座 (うお座)', 'en': 'Pisces', 'emoji': '♓'}
}

# キャッシュ / Cache for today's horoscopes (doesn't change during the day)
horoscope_cache = {}

def get_cache_key(sign_key, day, lang):
    """キャッシュキーを生成 / Generate cache key"""
    today = date.today().isoformat()
    return f"{today}_{sign_key}_{day}_{lang}"

def get_horoscope_from_api(sign_key, day='today'):
    """APIから占いを取得 / Get horoscope from API"""
    try:
        url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/{day}"
        params = {"sign": sign_key}
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('success'):
            return data['data']['horoscope_data']
        else:
            return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

def get_detailed_horoscope(sign_key, day, lang):
    """詳細な占いを生成 / Generate detailed horoscope"""
    
    # キャッシュをチェック / Check cache
    cache_key = get_cache_key(sign_key, day, lang)
    if cache_key in horoscope_cache:
        return horoscope_cache[cache_key]
    
    # APIから基本の占いを取得 / Get basic horoscope from API
    base_horoscope = get_horoscope_from_api(sign_key, day)
    
    # 詳細な占いを生成 / Generate detailed horoscope
    detailed = generate_detailed_horoscope(sign_key, day, lang, base_horoscope)
    
    # キャッシュに保存 / Save to cache
    horoscope_cache[cache_key] = detailed
    
    return detailed

def generate_detailed_horoscope(sign_key, day, lang, base_horoscope=None):
    """詳細な占いを生成 / Generate detailed horoscope with multiple sections"""
    
    # 日付を正しく設定 / Set correct date
    today = date.today()
    
    if day == 'today':
        target_date = today
        date_str_ja = target_date.strftime('%Y年%m月%d日')
        date_str_en = target_date.strftime('%B %d, %Y')
    else:
        target_date = today + timedelta(days=1)
        date_str_ja = target_date.strftime('%Y年%m月%d日')
        date_str_en = target_date.strftime('%B %d, %Y')
    
    # ラッキーアイテム / Lucky items (fixed for the date)
    random.seed(f"{sign_key}_{day}_{target_date.isoformat()}")
    
    lucky_numbers = random.sample(range(1, 50), 3)
    lucky_colors_ja = ['赤', '青', '黄色', '緑', '紫', '金', '銀', 'ピンク', 'オレンジ', '白']
    lucky_colors_en = ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Gold', 'Silver', 'Pink', 'Orange', 'White']
    lucky_items_ja = ['水晶', '翡翠', '真珠', 'ルビー', 'サファイア', 'オニキス', 'アメジスト', 'ターコイズ']
    lucky_items_en = ['Crystal', 'Jade', 'Pearl', 'Ruby', 'Sapphire', 'Onyx', 'Amethyst', 'Turquoise']
    
    lucky_color_ja = random.choice(lucky_colors_ja)
    lucky_color_en = random.choice(lucky_colors_en)
    lucky_item_ja = random.choice(lucky_items_ja)
    lucky_item_en = random.choice(lucky_items_en)
    
    # ラッキータイム / Lucky time
    lucky_hour_start = random.randint(10, 14)
    lucky_hour_end = lucky_hour_start + random.randint(2, 4)
    
    # 相性の良い星座 / Compatible signs
    compatible = {
        'aries': {'ja': '獅子座・射手座', 'en': 'Leo, Sagittarius'},
        'taurus': {'ja': '乙女座・山羊座', 'en': 'Virgo, Capricorn'},
        'gemini': {'ja': '天秤座・水瓶座', 'en': 'Libra, Aquarius'},
        'cancer': {'ja': '蠍座・魚座', 'en': 'Scorpio, Pisces'},
        'leo': {'ja': '牡羊座・射手座', 'en': 'Aries, Sagittarius'},
        'virgo': {'ja': '牡牛座・山羊座', 'en': 'Taurus, Capricorn'},
        'libra': {'ja': '双子座・水瓶座', 'en': 'Gemini, Aquarius'},
        'scorpio': {'ja': '蟹座・魚座', 'en': 'Cancer, Pisces'},
        'sagittarius': {'ja': '牡羊座・獅子座', 'en': 'Aries, Leo'},
        'capricorn': {'ja': '牡牛座・乙女座', 'en': 'Taurus, Virgo'},
        'aquarius': {'ja': '双子座・天秤座', 'en': 'Gemini, Libra'},
        'pisces': {'ja': '蟹座・蠍座', 'en': 'Cancer, Scorpio'}
    }
    
    # 詳細な占いコンテンツ / Detailed horoscope content
    if base_horoscope:
        main_ja = base_horoscope
        main_en = base_horoscope
    else:
        main_ja = get_detailed_ja_horoscope(sign_key, day)
        main_en = get_detailed_en_horoscope(sign_key, day)
    
    # セクションごとの占い / Section horoscopes
    if lang == 'ja':
        love_ja = get_love_horoscope_ja(sign_key, day)
        career_ja = get_career_horoscope_ja(sign_key, day)
        health_ja = get_health_horoscope_ja(sign_key, day)
        advice_ja = get_advice_ja(sign_key, day)
        
        sign_name = ZODIAC_SIGNS[sign_key]['ja']
        emoji = ZODIAC_SIGNS[sign_key]['emoji']
        compatible_text = compatible[sign_key]['ja']
        
        day_text = "今日" if day == 'today' else "明日"
        
        return f"""{emoji} *{sign_name} の{day_text}の運勢* {emoji}

📅 *{date_str_ja}*

━━━━━━━━━━━━━━━━━━━━━━

🔮 *総合運*
{main_ja}

━━━━━━━━━━━━━━━━━━━━━━

💖 *恋愛運*
{love_ja}

━━━━━━━━━━━━━━━━━━━━━━

💼 *仕事運*
{career_ja}

━━━━━━━━━━━━━━━━━━━━━━

🏃‍♂️ *健康運*
{health_ja}

━━━━━━━━━━━━━━━━━━━━━━

💫 *今日のアドバイス*
{advice_ja}

━━━━━━━━━━━━━━━━━━━━━━

✨ *ラッキーアイテム*
• 色: {lucky_color_ja}
• アイテム: {lucky_item_ja}
• 数字: {', '.join(map(str, lucky_numbers))}

💑 *相性の良い星座*
{compatible_text}

🌟 *ラッキータイム*
{lucky_hour_start}:00 - {lucky_hour_end}:00

━━━━━━━━━━━━━━━━━━━━━━
✨ 素敵な一日をお過ごしください！ ✨"""
    
    else:
        love_en = get_love_horoscope_en(sign_key, day)
        career_en = get_career_horoscope_en(sign_key, day)
        health_en = get_health_horoscope_en(sign_key, day)
        advice_en = get_advice_en(sign_key, day)
        
        sign_name = ZODIAC_SIGNS[sign_key]['en']
        emoji = ZODIAC_SIGNS[sign_key]['emoji']
        compatible_text = compatible[sign_key]['en']
        
        day_text = "Today" if day == 'today' else "Tomorrow"
        
        return f"""{emoji} *{sign_name} Horoscope for {day_text}* {emoji}

📅 *{date_str_en}*

━━━━━━━━━━━━━━━━━━━━━━

🔮 *Overall Fortune*
{main_en}

━━━━━━━━━━━━━━━━━━━━━━

💖 *Love & Relationships*
{love_en}

━━━━━━━━━━━━━━━━━━━━━━

💼 *Career & Finance*
{career_en}

━━━━━━━━━━━━━━━━━━━━━━

🏃‍♂️ *Health & Wellness*
{health_en}

━━━━━━━━━━━━━━━━━━━━━━

💫 *Today's Advice*
{advice_en}

━━━━━━━━━━━━━━━━━━━━━━

✨ *Lucky Items*
• Color: {lucky_color_en}
• Item: {lucky_item_en}
• Numbers: {', '.join(map(str, lucky_numbers))}

💑 *Compatible Signs*
{compatible_text}

🌟 *Lucky Time*
{lucky_hour_start}:00 - {lucky_hour_end}:00

━━━━━━━━━━━━━━━━━━━━━━
✨ Have a wonderful day! ✨"""

def get_detailed_ja_horoscope(sign_key, day):
    """詳細な日本語占い / Detailed Japanese horoscope"""
    horoscopes = {
        'today': {
            'aries': "今日はあなたのエネルギーが最高潮に達する日です。\n\n新しいプロジェクトや挑戦を始めるのに最適なタイミングです。周囲の人々もあなたの情熱に引き寄せられ、協力を惜しまないでしょう。午前中は直感が鋭く、重要な決断を下すのに適しています。午後は人間関係がスムーズに進み、思いがけないサポートを得られるかもしれません。",
            'taurus': "今日は安定と成長のバランスが取れた一日です。\n\nこれまでの努力が実を結び始め、目に見える成果が出てくるでしょう。特に金運が上昇傾向にあり、長期的な投資や貯蓄に良い影響があります。心身ともにリラックスできる時間を作ることで、さらなる幸運を引き寄せられます。",
            'gemini': "コミュニケーションが鍵を握る一日です。\n\nあなたのアイデアや意見が多くの人に受け入れられ、思わぬ展開を生み出すでしょう。特にクリエイティブな仕事や勉強に集中すると良い結果が出ます。夕方以降は社交的な場での出会いが、将来につながるヒントを与えてくれます。"
        },
        'tomorrow': {
            'aries': "明日は忍耐が試される日です。\n\n急な展開には焦らず、一歩ずつ着実に進むことが大切です。人間関係では、相手の立場を理解することで、より深い信頼関係を築けるでしょう。午後になると状況が好転し、新しいチャンスが訪れる予感があります。",
            'taurus': "明日は創造性が高まる一日です。\n\n普段とは違う視点で物事を考えることで、新しい解決策が見つかるでしょう。アートや音楽など、創造的な活動に没頭するのに最適なタイミングです。夜はリラックスして、自分自身を労わる時間を作りましょう。"
        }
    }
    
    default = "今日は穏やかなエネルギーに包まれる一日です。\n\n無理をせず、自分のペースで物事を進めましょう。周囲からのサポートを受け入れ、感謝の気持ちを忘れずに。新しい出会いや発見があり、心が豊かになるでしょう。"
    
    if day == 'today':
        return horoscopes['today'].get(sign_key, default)
    else:
        return horoscopes['tomorrow'].get(sign_key, default)

def get_detailed_en_horoscope(sign_key, day):
    """Detailed English horoscope"""
    horoscopes = {
        'today': {
            'aries': "Today your energy reaches its peak.\n\nThis is the perfect time to start new projects or challenges. People around you will be drawn to your passion and won't hesitate to cooperate. Your intuition is sharp in the morning, making it ideal for important decisions. In the afternoon, relationships will flow smoothly, and you might receive unexpected support.",
            'taurus': "Today is a balanced day of stability and growth.\n\nYour hard work will begin to bear fruit, and you'll see tangible results. Your financial luck is rising, which positively affects long-term investments and savings. Creating time to relax both mentally and physically will attract even more good fortune.",
            'gemini': "Communication is key today.\n\nYour ideas and opinions will be well received by many, creating unexpected developments. Focusing on creative work or studying will yield good results. After sunset, social encounters will give you hints for the future."
        },
        'tomorrow': {
            'aries': "Tomorrow patience will be tested.\n\nDon't rush sudden developments; it's important to proceed steadily step by step. Understanding others' perspectives will help build deeper trust in relationships. In the afternoon, the situation will improve, and new opportunities may arise.",
            'taurus': "Tomorrow your creativity will be high.\n\nThinking from a different perspective will help find new solutions. This is the perfect time to immerse yourself in creative activities like art or music. In the evening, relax and take time to nurture yourself."
        }
    }
    
    default = "Today you will be surrounded by gentle energy.\n\nDon't push yourself too hard; proceed at your own pace. Accept support from others and don't forget to be grateful. New encounters and discoveries will enrich your heart."
    
    if day == 'today':
        return horoscopes['today'].get(sign_key, default)
    else:
        return horoscopes['tomorrow'].get(sign_key, default)

def get_love_horoscope_ja(sign_key, day):
    love = {
        'aries': "恋愛運は上昇傾向です。シングルの方は、思いがけない場所で素敵な出会いがありそうです。パートナーがいる方は、一緒に新しい体験をすることで絆が深まります。",
        'taurus': "今日は感情表現がスムーズにできる日です。気になっている人に思いを伝える良い機会になるでしょう。",
        'gemini': "会話が弾み、相手との距離が縮まります。デートやお出かけに最適な一日です。"
    }
    return love.get(sign_key, "穏やかな恋愛運です。相手を思いやる気持ちを大切にしましょう。")

def get_love_horoscope_en(sign_key, day):
    love = {
        'aries': "Your love luck is rising. Singles may encounter someone special in unexpected places. For those in relationships, trying new experiences together will deepen your bond.",
        'taurus': "Today expressing emotions comes easily. A good opportunity to share your feelings with someone you care about.",
        'gemini': "Conversations flow smoothly, bringing you closer to others. A perfect day for dates or going out."
    }
    return love.get(sign_key, "Your love luck is gentle. Value your caring feelings toward others.")

def get_career_horoscope_ja(sign_key, day):
    return "仕事運は良好です。これまでの努力が評価され、新しい責任やチャンスが訪れるでしょう。チームワークを大切にすることで、さらなる成功を掴めます。"

def get_career_horoscope_en(sign_key, day):
    return "Your career luck is good. Your efforts will be recognized, bringing new responsibilities and opportunities. Valuing teamwork will lead to further success."

def get_health_horoscope_ja(sign_key, day):
    return "健康運は安定しています。適度な運動とバランスの良い食事を心がけましょう。ストレスを溜め込まず、リラックスする時間を作ることが大切です。"

def get_health_horoscope_en(sign_key, day):
    return "Your health luck is stable. Aim for moderate exercise and a balanced diet. It's important not to hold onto stress and to make time to relax."

def get_advice_ja(sign_key, day):
    return "今日は直感を信じて行動してみましょう。普段と違う選択をすることで、新しい可能性が開けます。"

def get_advice_en(sign_key, day):
    return "Trust your intuition today. Making different choices than usual may open up new possibilities."

@app.route('/')
def index():
    return render_template('index.html', signs=ZODIAC_SIGNS)

@app.route('/horoscope', methods=['POST'])
def horoscope():
    data = request.json
    sign_key = data.get('sign')
    day = data.get('day', 'today')
    lang = data.get('lang', 'ja')
    
    message = get_detailed_horoscope(sign_key, day, lang)
    
    return jsonify({'horoscope': message})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)