"""
Helper functions for marker recommendations and explanations
"""

def get_marker_recommendation(marker_id, language="English"):
    """Get practical recommendations for improving a specific marker"""
    
    recommendations = {
        # C3: Establishes and Maintains Agreements
        "3.1": {
            "en": """**How to Demonstrate Marker 3.1:**
- Start every session by asking: "What would you like to focus on today?"
- Use phrases like: "What outcome would make this session valuable for you?"
- Explicitly partner: "Let's agree on what we want to accomplish in our time together"

**Practice Exercise:**  
Record yourself asking 3 different clients what they want from the session.""",
            "ar": """**كيف تُظهر Marker 3.1:**
- ابدأ كل جلسة بالسؤال: "على ماذا تريد أن نركز اليوم؟"
- استخدم عبارات مثل: "ما النتيجة التي ستجعل هذه الجلسة ذات قيمة لك؟"
- شارك بوضوح: "دعنا نتفق على ما نريد تحقيقه في وقتنا معاً"

**تمرين عملي:**  
سجل نفسك وأنت تسأل 3 عملاء مختلفين عما يريدون من الجلسة."""
        },
        "3.2": {
            "en": """**How to Demonstrate Marker 3.2:**
- Ask: "How will you know this session was successful?"
- Explore measurable outcomes: "What would be different if you achieve this?"
- Check clarity: "On a scale of 1-10, how clear are you on what success looks like?"

**Practice Phrase:**  
"By the end of our session, what specifically would you like to have accomplished?"""",
            "ar": """**كيف تُظهر Marker 3.2:**
- اسأل: "كيف ستعرف أن هذه الجلسة كانت ناجحة؟"
- استكشف النتائج القابلة للقياس: "ماذا سيكون مختلفاً إذا حققت هذا؟"
- تحقق من الوضوح: "على مقياس من 1-10، ما مدى وضوحك حول شكل النجاح؟"

**عبارة للممارسة:**  
"بنهاية جلستنا، ما الذي تود تحقيقه بشكل محدد؟"""",
        },
        "4.1": {
            "en": """**How to Demonstrate Marker 4.1:**
- Acknowledge client insights: "That's a really important observation you just made"
- Recognize their work: "I can see you've put a lot of thought into this"
- Validate their process: "The way you approached this shows real self-awareness"

**Key Principle:**  
Trust the client as the expert on their own life.""",
            "ar": """**كيف تُظهر Marker 4.1:**
- اعترف برؤى العميل: "هذه ملاحظة مهمة حقاً قمت بها للتو"
- اعترف بعملهم: "أرى أنك وضعت الكثير من التفكير في هذا"
- صدق على عمليتهم: "الطريقة التي اتبعتها تُظهر وعياً حقيقياً بالذات"

**المبدأ الأساسي:**  
ثق بالعميل كخبير في حياته الخاصة."""
        },
        "5.5": {
            "en": """**How to Demonstrate Marker 5.5:**
- After asking a powerful question, COUNT TO 7 before speaking again
- Notice client's thinking process - don't rush to fill silence
- Say: "Take all the time you need" when client is reflecting

**Common Mistake:**  
Rushing to rephrase questions destroys valuable thinking space.""",
            "ar": """**كيف تُظهر Marker 5.5:**
- بعد طرح سؤال قوي، عُد حتى 7 قبل التحدث مرة أخرى
- لاحظ عملية تفكير العميل - لا تستعجل لملء الصمت
- قل: "خذ كل الوقت الذي تحتاجه" عندما يفكر العميل

**خطأ شائع:**  
الاستعجال في إعادة صياغة الأسئلة يدمر مساحة التفكير القيمة."""
        },
        "6.2": {
            "en": """**How to Demonstrate Marker 6.2:**
- Client says "stuck" - ask: "What does 'stuck' mean for you?"
- Client uses metaphor - explore it: "Tell me more about that 'wall' you mentioned"
- Pick specific words: "You said 'should' - whose voice is that?"

**Power Move:**  
Repeat client's exact word back as a question.""",
            "ar": """**كيف تُظهر Marker 6.2:**
- يقول العميل "عالق" - اسأل: "ماذا يعني 'عالق' بالنسبة لك؟"
- يستخدم العميل استعارة - استكشفها: "أخبرني المزيد عن ذلك 'الجدار'"
- اختر كلمات محددة: "قلت 'يجب' - صوت من هذا؟"

**حركة قوية:**  
كرر كلمة العميل المحددة كسؤال."""
        },
        "7.6": {
            "en": """**How to Demonstrate Marker 7.6:**
- Ask ONE question at a time
- Use open questions: What, How, Who (not Why)
- Pause 3-5 seconds between questions

**Bad Example:** "What's your goal and how will you achieve it?"  
**Good Example:** "What's your goal?" [WAIT FOR ANSWER]""",
            "ar": """**كيف تُظهر Marker 7.6:**
- اطرح سؤالاً واحداً في المرة
- استخدم أسئلة مفتوحة: ماذا، كيف، من (وليس لماذا)
- توقف 3-5 ثوانٍ بين الأسئلة

**مثال سيء:** "ما هدفك وكيف ستحققه؟"  
**مثال جيد:** "ما هدفك؟" [انتظر الإجابة]"""
        },
        "8.5": {
            "en": """**How to Demonstrate Marker 8.5:**
- Ask: "What will you do after our session?"
- Explore: "How would you like to capture your insights?"
- Partner: "Would it be helpful to have an action step?"

**Framework:**  
Always ASK if they want next steps rather than ASSIGN them.""",
            "ar": """**كيف تُظهر Marker 8.5:**
- اسأل: "ماذا ستفعل بعد جلستنا؟"
- استكشف: "كيف تريد التقاط رؤاك؟"
- شارك: "هل سيكون من المفيد أن يكون لديك خطوة عمل؟"

**الإطار:**  
اسأل دائماً إذا كانوا يريدون الخطوات التالية."""
        }
    }
    
    # Default recommendation
    default = {
        "en": f"""**To improve Marker {marker_id}:**
1. Review the ICF PCC Markers document for exact behavior
2. Practice the specific language for this marker
3. Record sessions and identify where you could demonstrate it
4. Focus on ONE marker per practice session

**Key Question:** "How can I partner MORE with my client here?"""",
        "ar": f"""**لتحسين Marker {marker_id}:**
1. راجع وثيقة ICF PCC Markers للسلوك الدقيق
2. مارس اللغة المحددة لهذا الماركر
3. سجل الجلسات وحدد أين كان بإمكانك إظهاره
4. ركز على ماركر واحد لكل جلسة تدريب

**السؤال الأساسي:** "كيف يمكنني الشراكة أكثر مع عميلي؟""""
    }
    
    marker_rec = recommendations.get(marker_id, default)
    return marker_rec["ar"] if language == "العربية" else marker_rec["en"]


def get_marker_explanation(marker_id, comp_id, language="English"):
    """Get detailed explanation of what a marker means"""
    
    explanations = {
        "3.1": {
            "en": """**Marker 3.1: Session Goal Agreement**

This marker checks if the coach actively partners with the client to establish what the client wants to accomplish in THIS specific session.

**What it looks for:**  
- Coach explicitly asks about session goals
- Client states what they want to work on  
- There's clear agreement (not coach deciding)

**Why it matters:** Without clear session goals, coaching can wander.""",
            "ar": """**Marker 3.1: اتفاقية هدف الجلسة**

هذا الماركر يتحقق من أن المدرب يشارك العميل بنشاط لتحديد ما يريد العميل تحقيقه في هذه الجلسة المحددة.

**ما الذي يبحث عنه:**  
- المدرب يسأل صراحةً عن أهداف الجلسة  
- العميل يذكر ما يريد العمل عليه  
- هناك اتفاق واضح (وليس قرار المدرب)

**لماذا هذا مهم:** بدون أهداف واضحة، يمكن أن يتشتت التدريب."""
        },
        "5.5": {
            "en": """**Marker 5.5: Allowing Silence**

This marker evaluates if the coach creates space for client thinking by allowing silence, pauses, or reflection.

**What it looks for:**  
- Coach doesn't interrupt client's thinking  
- Natural pauses exist in the conversation  
- Coach waits for client to complete thought process

**Why it matters:** Deep insights emerge from reflection. Silence is powerful.""",
            "ar": """**Marker 5.5: السماح بالصمت**

هذا الماركر يقيّم ما إذا كان المدرب يخلق مساحة لتفكير العميل من خلال السماح بالصمت أو التوقفات.

**ما الذي يبحث عنه:**  
- المدرب لا يقاطع تفكير العميل  
- توجد توقفات طبيعية في المحادثة  
- المدرب ينتظر العميل لإكمال عملية تفكيره

**لماذا هذا مهم:** الرؤى العميقة تنبثق من التأمل. الصمت قوي."""
        },
        "7.6": {
            "en": """**Marker 7.6: Clear, Direct Questions**

This marker assesses the quality and delivery of the coach's questions.

**What it looks for:**  
- Questions are open-ended (not yes/no)  
- ONE question at a time  
- Coach pauses to let client think  
- Questions are clear and direct

**Why it matters:** Quality questions create quality thinking. This is THE most common PCC failure point.""",
            "ar": """**Marker 7.6: أسئلة واضحة ومباشرة**

هذا الماركر يقيّم جودة وطريقة تقديم أسئلة المدرب.

**ما الذي يبحث عنه:**  
- الأسئلة مفتوحة (وليست نعم/لا)  
- سؤال واحد في المرة  
- المدرب يتوقف ليسمح للعميل بالتفكير  
- الأسئلة واضحة ومباشرة

**لماذا هذا مهم:** الأسئلة الجيدة تخلق تفكيراً جيداً. هذه أكثر نقطة فشل شيوعاً في PCC."""
        }
    }
    
    default = {
        "en": f"""**Marker {marker_id} belongs to {comp_id}**

This marker assesses a specific OBSERVABLE behavior that demonstrates coaching competency.  
Review the ICF PCC Markers document for the complete definition.

**Key Principle:** PCC assessment is about OBSERVABLE BEHAVIORS, not subjective quality.""",
        "ar": f"""**Marker {marker_id} ينتمي إلى {comp_id}**

هذا الماركر يقيّم سلوكاً محدداً يمكن ملاحظته يُظهر كفاءة التدريب.  
راجع وثيقة ICF PCC Markers للتعريف الكامل.

**المبدأ الأساسي:** تقييم PCC يتعلق بالسلوكيات التي يمكن ملاحظتها، وليس الجودة الذاتية."""
    }
    
    marker_exp = explanations.get(marker_id, default)
    return marker_exp["ar"] if language == "العربية" else marker_exp["en"]
