from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
import google.generativeai as genai
from backend.config import settings
from backend.models.db_models import ScrapedArticle, DomainAnalysis, TopicAnalysis, Language
from typing import List
from datetime import date, datetime
import json
import re
from backend.models.ai_models import CrossSourceAnalysis
from backend.models.ai_models import DomainAnalysisLLM, TopicAnalysisLLM
from backend.models.enums import PoliticalLeaning, Sentiment

#load .env
from dotenv import load_dotenv
import os
import sys
load_dotenv()

gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment variables.")

# Create LLM client using Langchain
try:
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=gemini_api_key,
        temperature=settings.GEMINI_TEMPERATURE
    )
except Exception as e:
    print(f"Error initializing ChatGoogleGenerativeAI: {e}")
    sys.exit(1)


narrative_template = ChatPromptTemplate.from_messages([
    ("system", """
        You are the Editor-in-Chief at MagyarMa.
        Your task is to process the provided Hungarian article excerpts and generate TWO distinct outputs:
        1. A very short, neutral summary (1-2 sentences) suitable for a preview card.
        2. A detailed, structured daily news narrative (approx. 400-500 words).

        Both outputs must be in {language}, strictly neutral, unbiased, and based **only** on the facts and focus of the supplied excerpts.
        Do **not** add any extra commentary, emotion, or opinion. Preserve the original tone and emphasis.
        The detailed narrative must follow the specified section structure and be written as continuous prose.
        Crucially, your entire output **must** use the specified markers for parsing.
    """),
    ("user", """
        Kérem, készítsen két részből álló kimenetet a mai cikkrészletekből:

        **1. RÉSZ: Rövid Összefoglaló**
        - Kezdje a `[START_SHORT_SUMMARY]` markerrel.
        - Írjon egy rendkívül tömör, 1-2 mondatos semleges összefoglalót a nap legfontosabb híreiről (csak a cikkek alapján). Ez egy előnézeti kártyára kerül.
        - Zárja a `[END_SHORT_SUMMARY]` markerrel.

        **2. RÉSZ: Részletes Napi Hírfolyam**
        - Kezdje a `[START_MAIN_SUMMARY]` markerrel.
        - Írjon egy jól szerkesztett, objektív, kb. 400–500 szavas napi összefoglalót valódi cikk-szövegként (nincsenek listák).
        - Tartsa meg az alábbi **szerkezetet**, és **minden szekció tartalmát** tegye a megadott markerek közé:

            `[START_BEVEZETO]`
            **Bevezető**
            Egy-két mondatban foglalja össze az aznapi legfontosabb, majd részletezésre kerülő történéseket semleges hangnemben. (Csak azokat a témákat említse, amelyeket később valóban kibont.)
            `[END_BEVEZETO]`

            `[START_BELFOLD]`
            **Belföld**
            Ismertesse a kiemelt hazai politikai és közéleti eseményeket világos átvezetések mellett („Eközben…", „Ugyanakkor…"). Ha nincs releváns belföldi hír a cikkekben, hagyja üresen a markerek között.
            `[END_BELFOLD]`

            `[START_KULFOLD]`
            **Külföld**
            Mutassa be a legfontosabb nemzetközi fejleményeket (diplomácia, háborúk, gazdasági konfliktusok). Ha nincs releváns külföldi hír a cikkekben, hagyja üresen a markerek között.
            `[END_KULFOLD]`

            `[START_TARSADALOM]`
            **Társadalom, kultúra, tudomány**
            Ha van releváns anyag (pl. fotópályázat, egészségügyi kutatás, kulturális esemény stb.), építse ebbe a szekcióba. Ha nincs, hagyja üresen a markerek között.
            `[END_TARSADALOM]`

            `[START_ZARAS]`
            **Zárás**
            Egyetlen tömör bekezdésben vonja össze a fenti információkat anélkül, hogy új ötletet vagy jövőre utalást tenne.
            `[END_ZARAS]`

        - Zárja az egész részt a `[END_MAIN_SUMMARY]` markerrel.

        FONTOS KIKÖTÉSEK A RÉSZLETES HÍRFOLYAMRA:
        - Szigorúan tilos érzelmi töltetű vagy értékelő megjegyzéseket írni.
        - Kerülje a költői vagy "felpörgető" nyelvezetet.
        - Kizárólag a megadott cikkek tényszerű állításaira támaszkodjon.
        - A szekciók címeit (**Bevezető**, **Belföld** stb.) **ne** írja bele a generált szövegbe, csak a markereket használja a tartalom köré.
        - A kimenetet {language} nyelven adja meg.

        --- START OF ARTICLES ---
        {articles_text}
        --- END OF ARTICLES ---
    """),
])

domain_topic_template = ChatPromptTemplate.from_messages([
    ("system", """
        You are an expert media analyst specializing in Hungarian news content.
        Your task is to identify key topics from articles from a single news source
        and determine the sentiment and political leaning in their reporting.
        You will return a structured analysis in {language} that can be processed automatically.
    """),
    ("user", """
        Analyze these Hungarian news articles from {domain} and identify around 10 important topics.
        
        For your output, provide:
        1. The domain name (exactly as provided to you)
        2. A list of topics with the following information for each:
           - A concise topic name in {language}
           - The sentiment (must be exactly one of: "pozitív", "negatív", or "semleges")
           - The political leaning (must be exactly one of: "bal", "közép-bal", "közép", "közép-jobb", "jobb")
           - 1-2 key phrases that demonstrate the framing in {language}
           - A brief analysis of how the topic was framed in {language}
           - The EXACT full URLs of articles that discuss this topic (copy them exactly as provided)
        
        It is very important that you only select approximately 10 most relevant topics with the highest importance.
        
        --- START OF ARTICLES ---
        {articles_text}
        --- END OF ARTICLES ---
    """),
])


cross_source_template = ChatPromptTemplate.from_messages([
    ("system", """
        You are an expert media analyst specializing in Hungarian news content and political bias analysis.
        Your task is to identify common topics across different news sources and analyze how each source
        covers the same events with different perspectives, sentiment, and political leanings.
        You must write your entire analysis in {language}.
     
     CRITICAL: Your output must strictly follow the Pydantic model structure.
        For EACH unified topic, you MUST include ALL required fields including:
        - name
        - source_coverage (with all its nested required fields)
        - comparative_analysis (this field is REQUIRED for every topic and must provide actual analysis)
        
        Never omit required fields from the structure.
    """),
    ("user", """
        Elemezd a következő téma adatokat a különböző magyar hírforrásokból {date} napra vonatkozóan.
        Találd meg azt a max. 5-6 legfontosabb témát, amelyeket több forrás is lefed, ideális esetben
        azokat amikről a legtöbb helyen készült cikk és elemezd a különbségeket
        a hangvételben, politikai beállítottságban és keretezésben.
        
        Minden közös témára vonatkozóan:
        1. Hozz létre egy egységesített témanevet {language} nyelven
        2. Sorold fel, mely források foglalkoztak vele
        3. Hasonlítsd össze a hangvételt a források között (érték szigorúan a következők közül: "pozitív", "negatív", "semleges")
        4. Hasonlítsd össze a politikai keretezést a források között (érték szigorúan a következők közül: "bal", "közép-bal", "közép", "közép-jobb", "jobb")
        5. Emeld ki a keretezésben és nézőpontban tapasztalható főbb különbségeket {language} nyelven
        6. Ha esetleg egy cikk többször szerepelne a keretezésben, akkor csak egyszer említsd meg
        7. Add meg az eredeti cikkek URL-jeit, hogy azok elérhetőek legyenek az elemzésben
        
        KRITIKUS: A kimenetnek a következő Pydantic modell struktúrát KELL követnie:
        
        ```python
        class SourceCoverage(BaseModel):
            domain: str  # A forrás domain neve (pl. telex, origo)
            original_topic_name: str  # A téma neve az adott forrásnál
            sentiment: str  # A hangvétel (pontosan így: "pozitív", "negatív", vagy "semleges")
            political_leaning: str  # Politikai beállítottság (pontosan így: "bal", "közép-bal", "közép", "közép-jobb", "jobb")
            key_phrases: List[str]  # Kulcsmondatok
            framing: str  # A téma keretezésének elemzése
            article_urls: List[str]  # A cikkek URL-jei
        
        class UnifiedTopic(BaseModel):
            name: str  # Az egységesített téma neve
            source_coverage: List[SourceCoverage]  # A források lefedettsége
            comparative_analysis: str  # Összehasonlító elemzés a források között - KÖTELEZŐ KITÖLTENI!
        
        class CrossSourceAnalysis(BaseModel):
            date: str  # Az elemzés dátuma
            unified_topics: List[UnifiedTopic]  # Egységesített témák listája
            language: str  # Az elemzés nyelve ("hu" vagy "en")
        ```
     
        Nagyon fontos hogy csak a legfontosabb kivonatokat (laponként max 2-3-at, többet ne) említs meg egy témához,
        és ebben a helyzetben is összegezd ezeket egyetlen "source coverage" részben, hogy ne legyenek redundánsak.
        Különösen figyelj arra, hogy egy unified topicc részben ne szerepeljen több source coverage ugyanazzal a domainnel,
        ilyenkor mindig fűzd össze a releváns információt domainenként egy "cource coverage" részbe
        
        Az elemzésed {language} nyelven készüljön.
        
        Íme a témaelemzések az egyes forrásokból:
        
        {source_data}
    """)
])

translate_cross_source_analysis_template = ChatPromptTemplate.from_messages([
    ("system", """
        You are an expert multilingual translator and media analyst.
        Your task is to translate a given CrossSourceAnalysis JSON object from {source_lang} to {target_lang}.
        You must translate ALL user-facing textual content while preserving the JSON structure.

        Specifically, translate the following fields:
        - In each 'UnifiedTopic': 'name', 'comparative_analysis'.
        - In each 'SourceCoverage' (within 'unified_topics'): 'original_topic_name', 'framing'.
        - Each string within the 'key_phrases' list in 'SourceCoverage'.

        The following fields MUST remain UNCHANGED (DO NOT TRANSLATE):
        - In each 'SourceCoverage': 'domain', 'article_urls', 'sentiment', 'political_leaning'.
        - The top-level 'date' field.
     
        It is absolutely crucial, that you translate all the unified topics, and put them in the output
        in the same order, as they are in the input

        The 'language' field in the root of the output JSON object MUST be set to '{target_lang}'.
        The output must be a valid JSON object that conforms to the CrossSourceAnalysis structure.
        Do not add any explanations or commentary outside the JSON structure.
    """),
    ("user", """
        Please translate the following CrossSourceAnalysis JSON object from {source_lang} to {target_lang}.
        Ensure all specified text fields are translated accurately, maintaining the original meaning and context.

        Input JSON ({source_lang}):
        ```json
        {input_analysis_json}
        ```
    """)
])

class LLMService:  
    @staticmethod
    def summarize_multiple_articles(articles: List[ScrapedArticle], language: Language = "hu") -> str:
        """
        Generates a single, thorough summary in Hungarian from a list of ScrapedArticle objects.

        Args:
            articles: A list of ScrapedArticle SQLAlchemy model instances.

        Returns:
            A string containing the generated summary.
        """
        if not articles:
            return "No articles provided to summarize."

        # Combine relevant text from each article
        combined_text = ""
        for i, article in enumerate(articles):
            combined_text += f"Article {i+1} (Source: {article.domain}, URL: {article.url}):\n"
            combined_text += f"Title: {article.title}\n"
            combined_text += f"Content: {article.content}\n\n" # Add separation between articles

        #dump the text into a txt file for debugging
        with open("context.txt", "w", encoding="utf-8") as f:
            f.write(combined_text)
        try:
            # Create the prompt
            prompt = narrative_template.invoke({
                "articles_text": combined_text,
                "language": language
                })

            # Invoke the LLM
            print(f"Invoking LLM for {language} summarization...")
            response = llm.invoke(prompt)
            print(f"LLM invocation complete for {language} summary.")

            with open("response.txt", "w", encoding="utf-8") as f:
                f.write(response.content)

            return response.content

        except Exception as e:
            print(f"Error during LLM summarization: {e}")
            return f"Error generating summary: {e}"


    @staticmethod
    def extract_domain_topics(articles: List[ScrapedArticle], language: Language = "hu") -> DomainAnalysis:
        """
        Extracts topics and sentiment from articles of a single domain.
        
        Args:
            articles: List of ScrapedArticle objects from a single domain
            
        Returns:
            DomainAnalysis object containing the domain, date, and topics.
        """
        if not articles or len(articles) == 0:
            return DomainAnalysis(
            domain="unknown", 
            date=datetime.now().date(), 
            topics=[]
        )
            
        domain = articles[0].domain
        
        combined_text = ""
        for i, article in enumerate(articles):
            combined_text += f"Article {i+1}:\n"
            combined_text += f"Title: {article.title}\n"
            combined_text += f"Content: {article.content}\n"
            combined_text += f"URL: {article.url}\n\n"
            
        try:
            # Create the prompt with domain specified
            prompt = domain_topic_template.invoke({
                "domain": domain,
                "articles_text": combined_text,
                "language": language
            })

            structured_llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=gemini_api_key,
                temperature=settings.GEMINI_TEMPERATURE
            ).with_structured_output(DomainAnalysisLLM)
            
            # Invoke the LLM
            print(f"Extracting topics for domain: {domain}...")
            response = structured_llm.invoke(prompt)
            
            # Save response for debugging with domain name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            with open(f"domain_topics_{domain}_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(response.model_dump_json(indent=2))

                
            topic_objects = []
            for topic_data in response.topics:
                topic_obj = TopicAnalysis(
                    topic=topic_data.topic,
                    political_leaning=topic_data.political_leaning,
                    sentiment=topic_data.sentiment,
                    framing=topic_data.framing,
                    key_phrases=topic_data.key_phrases,
                    article_urls=topic_data.article_urls
                )
                topic_objects.append(topic_obj)
                
            return DomainAnalysis(
                domain=domain,
                date=datetime.now().date(),
                topics=topic_objects,
                language=language
            )
                    
        except Exception as e:
            print(f"Error extracting topics for {domain}: {e}")
            import traceback
            traceback.print_exc()
            return DomainAnalysis(
                domain=domain, 
                date=datetime.now().date(), 
                topics=[],
                language = language
            )
        
    @staticmethod
    def translate_text(text_to_translate: str, source_lang: str, target_lang: str) -> str:
        """
        Translates text from a source language to a target language using an LLM.

        Args:
            text_to_translate: The text to be translated.
            source_lang: The source language code (e.g., "hu").
            target_lang: The target language code (e.g., "en").

        Returns:
            The translated text, or an error message string if translation fails.
        """
        if not text_to_translate:
            return ""
        if source_lang == target_lang:
            return text_to_translate

        try:
            prompt_text = (
                f"Translate the following text accurately from {source_lang} to {target_lang}. "
                f"Preserve the original meaning and tone. "
                f"CRITICAL: The formatting of the original text, including paragraph breaks, line breaks, "
                f"and any existing bracketed markers (e.g., `[EXAMPLE_MARKER]`), MUST be preserved EXACTLY "
                f"in the translated output. Do NOT translate the bracketed markers themselves; "
                f"they should appear verbatim in the output. "
                f"Provide ONLY the translated text. Do not add any of your own commentary, explanations, "
                f"or any new markers not present in the original text. The output should be ready to use directly, "
                f"maintaining the same overall structure and format as the input."
                f"If the input is a json strocture, you must pay extra attention to keep its original structure,"
                f"only translating the required text in the process"
                f"Text to translate:\n"
                f"--- START OF TEXT ---\n"
                f"{text_to_translate}\n"
                f"--- END OF TEXT ---"
            )
            
            translation_llm = ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=gemini_api_key,
                temperature=0.2
            )

            response = translation_llm.invoke(prompt_text)
            translated_text = response.content.strip()
            
            print(f"Translation to '{target_lang}' complete.")
            return translated_text

        except Exception as e:
            print(f"Error during text translation from '{source_lang}' to '{target_lang}': {e}")
            import traceback
            traceback.print_exc()
            return f"Error translating to {target_lang}: {e}"

    @staticmethod
    def translate_cross_Source_analysis(analysis_to_translate: CrossSourceAnalysis, source_lang: str, target_lang: str) -> CrossSourceAnalysis:
        """
        Translates all textual content within a CrossSourceAnalysis object from a source language
        to a target language using an LLM with structured output.

        Args:
            analysis_to_translate: The CrossSourceAnalysis object to translate.
            source_lang: The source language code (e.g., "hu").
            target_lang: The target language code (e.g., "en").

        Returns:
            A new CrossSourceAnalysis object with translated content and updated language field.
            Returns the original object if source_lang and target_lang are the same.
            Returns an empty CrossSourceAnalysis object on error.
        """
        if source_lang == target_lang:
            return analysis_to_translate

        if not analysis_to_translate or not analysis_to_translate.unified_topics:
            print(f"Warning: No data in CrossSourceAnalysis to translate from {source_lang} to {target_lang}.")
            return CrossSourceAnalysis(
                date=analysis_to_translate.date if analysis_to_translate else date.today().isoformat(),
                unified_topics=[],
                language=target_lang
            )

        try:
            input_analysis_dict = analysis_to_translate.model_dump()
            if isinstance(input_analysis_dict.get("date"), date):
                input_analysis_dict["date"] = input_analysis_dict["date"].isoformat()
            
            input_analysis_json = json.dumps(input_analysis_dict, ensure_ascii=False, indent=2)

            prompt = translate_cross_source_analysis_template.invoke({
                "source_lang": source_lang,
                "target_lang": target_lang,
                "input_analysis_json": input_analysis_json
            })

            big_llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-preview-04-17",
                google_api_key=gemini_api_key,
                temperature=settings.GEMINI_TEMPERATURE
            )
            structured_llm = big_llm.with_structured_output(CrossSourceAnalysis)

            print(f"Translating CrossSourceAnalysis from '{source_lang}' to '{target_lang}' for date {analysis_to_translate.date}...")
            translated_analysis = structured_llm.invoke(prompt)

            #save the analysis in txt for debugging
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            with open(f"translated_cross_source_analysis_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(translated_analysis.model_dump_json(indent=2, exclude_none=True))

            if translated_analysis:
                translated_analysis.language = target_lang
                translated_analysis.date = analysis_to_translate.date
                print(f"CrossSourceAnalysis successfully translated to '{target_lang}'.")
                return translated_analysis
            else:
                raise ValueError("LLM returned an empty or invalid translated analysis.")

        except Exception as e:
            print(f"Error during CrossSourceAnalysis translation from '{source_lang}' to '{target_lang}': {e}")
            import traceback
            traceback.print_exc()
            return CrossSourceAnalysis(
                date=analysis_to_translate.date if analysis_to_translate else date.today().isoformat(),
                unified_topics=[],
                language=target_lang
            )
        
    @staticmethod
    def cross_source_analysis(date: str, source_data: str, language: Language = "hu") -> CrossSourceAnalysis:
        """
        Analyzes topics across different sources for a given date.
        
        Args:
            date: The date of the articles in 'YYYY-MM-DD' format.
            source_data: List of DomainAnalysis objects from different sources.
            
        Returns:
            CrossSourceAnalysis object containing the cross-source analysis results.
        """
        try:

            prompt = cross_source_template.invoke({
                "date": date,
                "source_data": source_data,
                "language": language
            })

            # Initialize the LLM
            big_llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-preview-04-17",
                google_api_key=gemini_api_key,
                temperature=settings.GEMINI_TEMPERATURE
            )
            
            # Set up structured output
            structured_llm = big_llm.with_structured_output(CrossSourceAnalysis)
            
            result = structured_llm.invoke(prompt)
            
            # Save for debugging
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            with open(f"cross_source_analysis_{timestamp}.txt", "w", encoding="utf-8") as f:
                f.write(str(result))
            
            return result
            
        except Exception as e:
            print(f"Error during cross-source analysis: {e}")
            import traceback
            traceback.print_exc()
            
            # Return empty but valid CrossSourceAnalysis object
            return CrossSourceAnalysis(
                date=date,
                unified_topics=[],
                language=language
            )

llm_service = LLMService()