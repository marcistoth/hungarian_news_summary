from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
import google.generativeai as genai
from backend.config import settings
from backend.models.db_models import ScrapedArticle
from typing import List

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


multi_article_summary_template = ChatPromptTemplate.from_messages([
    ("system", "You are an expert news summarizer. Your task is to synthesize information from the provided collection of "
               "news articles and generate a single, coherent, and thorough summary. Focus on the main events, key figures, "
               "significant developments, and overall narrative presented across the articles. Avoid simply listing summaries "
               "of individual articles; instead, integrate the information into a unified overview. "
               "The summary should be written in Hungarian ('magyarul'). "
               "Structure the summary clearly, perhaps using bullet points for distinct topics if helpful. "
               "Try to be unbiased regarding everything, and to give back the exact style and tone of the articles as much as possible."),
    ("user", "Please provide a thorough summary in Hungarian based on the following articles:\n\n"
             "--- START OF ARTICLES ---\n"
             "{articles_text}"
             "\n--- END OF ARTICLES ---")
])

narrative_template = ChatPromptTemplate.from_messages([
    ("system", """
        You are the Editor-in-Chief at MagyarMa.
        Your task is to process the provided Hungarian article excerpts and generate TWO distinct outputs:
        1. A very short, neutral summary (1-2 sentences) suitable for a preview card.
        2. A detailed, structured daily news narrative (approx. 400-500 words).

        Both outputs must be in Hungarian, strictly neutral, unbiased, and based **only** on the facts and focus of the supplied excerpts.
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
            Ismertesse a kiemelt hazai politikai és közéleti eseményeket világos átvezetések mellett („Eközben…”, „Ugyanakkor…”). Ha nincs releváns belföldi hír a cikkekben, hagyja üresen a markerek között.
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
        - Kerülje a költői vagy “felpörgető” nyelvezetet.
        - Kizárólag a megadott cikkek tényszerű állításaira támaszkodjon.
        - A szekciók címeit (**Bevezető**, **Belföld** stb.) **ne** írja bele a generált szövegbe, csak a markereket használja a tartalom köré.

        --- START OF ARTICLES ---
        {articles_text}
        --- END OF ARTICLES ---
    """),
])

class LLMService:  
    @staticmethod
    def summarize_multiple_articles(articles: List[ScrapedArticle]) -> str:
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
            prompt = narrative_template.invoke({"articles_text": combined_text})

            # Invoke the LLM
            print("Invoking LLM for summarization...")
            response = llm.invoke(prompt)
            print("LLM invocation complete.")

            with open("response.txt", "w", encoding="utf-8") as f:
                f.write(response.content)

            return response.content

        except Exception as e:
            print(f"Error during LLM summarization: {e}")
            return f"Error generating summary: {e}"

llm_service = LLMService()