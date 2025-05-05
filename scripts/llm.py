from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
import google.generativeai as genai
from backend.config import settings
from backend.models.db_models import ScrapedArticle, DomainAnalysis, TopicAnalysis
from typing import List
from datetime import datetime
import json
import re
from backend.models.ai_models import CrossSourceAnalysis

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

domain_topic_template = ChatPromptTemplate.from_messages([
    ("system", """
        You are an expert media analyst specializing in Hungarian news content.
        Your task is to identify key topics from articles from a single news source
        and determine the sentiment and political leaning in their reporting.
    """),
    ("user", """
        Analyze these Hungarian news articles from {domain} and identify around 10 important topics.
        For each topic:
        1. Provide a concise topic name in Hungarian
        2. Analyze the sentiment (positive, negative, or neutral)
        3. Identify the political leaning (left, center-left, center, center-right, right)
        4. Extract 1-2 key phrases that demonstrate the framing
        5. Include the EXACT full URLs of articles that discuss this topic (copy them exactly as provided in the input)
        
        Return a JSON array with this structure:
        [
          {{
            "topic": "Topic name",
            "sentiment": "pozitív|negatív|semleges",
            "political_leaning": "bal|közép-bal|közép|közép-jobb|jobb",
            "key_phrases": ["idézet1", "idézet2"],
            "framing": "Hogyan keretezték a témát",
            "article_urls": ["https://full.url.com/article1", "https://full.url.com/article2"]
          }}
        ]
        
        Focus on clear topic identification that can be matched across different sources later.
     
        It is very important that you only select approximately the 10 most relevant topics from the articles, 
        with the highest magnitude, and importance.
        
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
        You must write your entire analysis in Hungarian language.
    """),
    ("user", """
        Elemezd a következő téma adatokat a különböző magyar hírforrásokból {date} napra vonatkozóan.
        Találd meg azt a max. 5-6 legfontosabb témát, amelyeket több forrás is lefed, ideális esetben
        azokat amikről a legtöbb helyen készült cikk és elemezd a különbségeket
        a hangvételben, politikai beállítottságban és keretezésben.
        
        Minden közös témára vonatkozóan:
        1. Hozz létre egy egységesített témanevet
        2. Sorold fel, mely források foglalkoztak vele
        3. Hasonlítsd össze a hangvételt (pozitív, negatív, semleges) a források között
        4. Hasonlítsd össze a politikai keretezést (bal, közép, jobb) a források között
        5. Emeld ki a keretezésben és nézőpontban tapasztalható főbb különbségeket
        6. Ha esetleg egy cikk többször szerepelne a keretezésben, akkor csak egyszer említsd meg
        7. Add meg az eredeti cikkek URL-jeit, hogy azok elérhetőek legyenek az elemzésben
        
        Az elemzésedet a megadott struktúrában add vissza:
     
        {{
          "date": "{date}",
          "unified_topics": [
            {{
              "name": "Egységesített téma neve",
              "source_coverage": [
                {{
                  "domain": "forrás_neve",
                  "original_topic_name": "Az adott forrás által használt eredeti témanév",
                  "sentiment": "hangvétel az adott forrásban",
                  "political_leaning": "politikai beállítottság",
                  "key_phrases": ["kulcsmondat1", "kulcsmondat2"],
                  "framing": "keretezés elemzése",
                  "article_urls": ["https://full.url.com/article1", "https://full.url.com/article2"]
                }}
              ],
              "comparative_analysis": "Elemzés arról, hogy az egyes források hogyan fedik le ugyanazt a témát különböző módon"
            }}
          ]
        }}
     
        Nagyon fontos hogy csak a legfontosabb kivonatokat (laponként max 2-3-at, többet ne) említs meg egy témához,
        és ebben a helyzetben is összegezd ezeket egyetlen "source coverage" részben, hogy ne legyenek redundánsak.
        Az elemzésed legyen világos és tömör, és kerüld a költői vagy "felpörgető" nyelvezetet.
        
        
        Íme a témaelemzések az egyes forrásokból:
        
        {source_data}
    """)
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


    @staticmethod
    def extract_domain_topics(articles: List[ScrapedArticle]) -> DomainAnalysis:
        """
        Extracts topics and sentiment from articles of a single domain.
        
        Args:
            articles: List of ScrapedArticle objects from a single domain
            
        Returns:
            DomainAnalysis object containing the domain, date, and topics.
        """
        if not articles or len(articles) == 0:
            return DomainAnalysis("unknown", datetime.now().date(), [])
            
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
                "articles_text": combined_text
            })
            
            # Invoke the LLM
            print(f"Extracting topics for domain: {domain}...")
            response = llm.invoke(prompt)
            
            # Save response for debugging with domain name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            with open(f"domain_topics_{domain}_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(response.content)
                
            try:
                raw_response = response.content
    
                # Find the first '[' and last ']' to extract just the JSON array
                start_idx = raw_response.find('[')
                end_idx = raw_response.rfind(']') + 1
                
                if start_idx != -1 and end_idx != -1:
                    # Extract the JSON array part
                    json_str = raw_response[start_idx:end_idx]
                    print(f"Extracted JSON: {json_str[:100]}...")
                    topics_data = json.loads(json_str)
                else:
                    print(f"No valid JSON array found in response: {raw_response[:100]}...")
                    topics_data = []
                # Convert to structured objects
                topic_objects = []
                for topic_data in topics_data:
                    topic_obj = TopicAnalysis(
                        topic=topic_data.get("topic", "not parseable"),
                        political_leaning=topic_data.get("political_leaning", "közép"),
                        sentiment=topic_data.get("sentiment", "semleges"),
                        framing=topic_data.get("framing", ""),
                        key_phrases=topic_data.get("key_phrases", []),
                        article_urls=topic_data.get("article_urls", [])
                    )
                    topic_objects.append(topic_obj)
                    
                # Create and return the domain analysis object
                return DomainAnalysis(
                    domain=domain,
                    date=datetime.now().date(),
                    topics=topic_objects
                )
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from LLM response: {e}")
                return DomainAnalysis(domain, datetime.now().date(), [])
                
        except Exception as e:
            print(f"Error extracting topics for {domain}: {e}")
            return DomainAnalysis(domain, datetime.now().date(), [])
        
    @staticmethod
    def cross_source_analysis(date: str, source_data: str) -> CrossSourceAnalysis:
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
                "source_data": source_data
            })

            # Initialize the LLM
            big_llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-preview-04-17",
                google_api_key=gemini_api_key,
                temperature=settings.GEMINI_TEMPERATURE
            )
            
            # Set up structured output
            structured_llm = big_llm.with_structured_output(CrossSourceAnalysis)
            
            # Get structured response
            print(f"Cross-source analysis for date: {date}...")
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
                unified_topics=[]
            )

llm_service = LLMService()