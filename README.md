# **Inteligencia Agentica y Análisis de Contexto Geopolítico en el Trading Automático: Una Investigación sobre los Ecosistemas de Claude Code y Gemini 1.5**

La evolución del trading algorítmico hacia sistemas basados en inteligencia artificial generativa ha marcado el inicio de una era donde la capacidad de razonamiento semántico supera a la simple ejecución estadística. En este nuevo paradigma, herramientas como Claude Code y Gemini 1.5 Pro no se limitan a actuar como motores de ejecución, sino que funcionan como analistas de investigación integrales capaces de procesar la realidad geopolítica y el flujo constante de noticias corporativas para fundamentar decisiones de inversión complejas.1 Esta investigación detalla los repositorios, experiencias de uso y arquitecturas técnicas que están permitiendo a traders e instituciones transitar desde el análisis técnico tradicional hacia una inteligencia de mercado profundamente contextualizada en la realidad global.3

## **Arquitecturas de Agentes y Frameworks Multi-Modelo**

La implementación de sistemas de trading basados en noticias ha encontrado su expresión más avanzada en las arquitecturas de múltiples agentes. Estos sistemas descomponen el proceso de inversión en roles especializados que colaboran para sintetizar información heterogénea, mitigando los sesgos individuales y las alucinaciones de los modelos de lenguaje.3

### **El Ecosistema TradingAgents: Simulación de Mesas Institucionales**

Uno de los repositorios más robustos en este ámbito es TradingAgents, un framework que emula la dinámica de una firma de trading profesional mediante la implementación de trece agentes especializados.2 Este sistema organiza a los agentes en equipos con funciones claramente definidas, permitiendo una evaluación multidimensional de cada activo financiero.3

| Rol del Agente | Función Específica | Fuentes de Datos Primarias |
| :---- | :---- | :---- |
| Analista de Noticias | Monitoreo de eventos macroeconómicos y noticias corporativas | Yahoo Finance, Finnhub, Alpha Vantage 5 |
| Analista de Sentimiento | Evaluación del estado de ánimo del mercado en redes sociales | APIs de redes sociales, hilos de noticias 3 |
| Investigador Alcista | Defensa de argumentos a favor de la inversión | Reportes de crecimiento, indicadores positivos 3 |
| Investigador Bajista | Identificación de riesgos y señales negativas | Análisis de deuda, amenazas legales, volatilidad 2 |
| Gestor de Riesgos | Evaluación de volatilidad y liquidez del portafolio | Métricas de VaR, correlaciones de sector 3 |

La arquitectura de TradingAgents se distingue por su proceso dialéctico. Tras la recopilación de datos por parte de los analistas, se inicia un debate entre investigadores alcistas (Bull) y bajistas (Bear).5 Este enfrentamiento asegura que las decisiones de inversión no se basen únicamente en el sentimiento superficial de una noticia, sino que consideren el impacto a largo plazo de los fundamentales de la empresa y el contexto geopolítico subyacente.2 En pruebas empíricas sobre acciones de AAPL, GOOGL y AMZN, este enfoque multi-agente logró un rendimiento acumulado del 26.62% frente a estrategias tradicionales basadas en reglas como MACD o RSI, que mostraron retornos negativos o marginales en el mismo periodo.3

### **MarketSenseAI: Chain-of-Agents y Análisis de Contexto Global**

Otro caso de estudio fundamental es MarketSenseAI, un marco de trabajo diseñado para el análisis holístico de acciones mediante el uso de modelos como GPT-4 y Claude 3.5.7 A diferencia de los sistemas que solo procesan titulares, MarketSenseAI utiliza un enfoque de "Cadena de Agentes" (Chain-of-Agents) para digerir documentos de gran escala, como presentaciones 10-K ante la SEC, transcripciones de llamadas de ganancias e informes macroeconómicos de instituciones como Goldman Sachs y Morgan Stanley.7

El componente MarketDigest dentro de este sistema es particularmente relevante para el análisis de la realidad geopolítica. Este agente sintetiza informes de investigación biemanales para ofrecer una narrativa coherente sobre las políticas de los bancos centrales, las tendencias sectoriales y los eventos de impacto global, como conflictos internacionales o pandemias.9 Los resultados de MarketSenseAI en el S\&P 100 durante el periodo 2023-2024 mostraron retornos del 125.9%, superando significativamente el 73.5% del índice de referencia.7

## **Claude Code y el Protocolo de Contexto de Modelo (MCP)**

La aparición de Claude Code ha revolucionado la forma en que los traders interactúan con sus entornos de desarrollo. Al ser un agente residente en la terminal con capacidades de ejecución de shell y gestión de archivos, permite una integración directa entre el razonamiento de la IA y las herramientas de ejecución financiera.10

### **El Papel de MCP en la Adquisición de Datos de Noticias**

El Model Context Protocol (MCP) actúa como el sistema nervioso que conecta a Claude Code con fuentes externas de datos financieros y noticias. Mediante servidores MCP especializados, el agente puede realizar consultas complejas que antes requerían una navegación manual extensa.12

| Servidor MCP | Capacidades de Análisis de Noticias y Datos | Aplicación en Trading |
| :---- | :---- | :---- |
| Financial Datasets | Acceso a precios en tiempo real, presentaciones SEC y noticias | Análisis de impacto inmediato tras publicaciones regulatorias 13 |
| EODHD Financial API | Datos históricos, análisis técnico y macro indicadores | Backtesting de estrategias basadas en noticias históricas 14 |
| GitHub MCP | Interacción con repositorios y gestión de flujos de código | Automatización de actualizaciones de scripts de trading 12 |
| PostgreSQL MCP | Consultas directas a bases de datos de operaciones | Correlación de noticias con rendimientos pasados 12 |

Un trader que utiliza Claude Code puede ejecutar comandos como claude analyze para procesar una carpeta llena de archivos CSV de transacciones bancarias o noticias descargadas, pidiendo al agente que identifique patrones de gasto o sentimientos recurrentes en los titulares antes de proponer una estrategia.10 La capacidad de Claude para "leer" el entorno local permite que el agente detecte inconsistencias en los datos de entrada o sugiera mejoras en la lógica de procesamiento de noticias en tiempo real.10

### **Claude Trading Skills: Modularidad en la Investigación**

El repositorio claude-trading-skills ofrece un ejemplo práctico de cómo dotar a Claude de capacidades específicas para el mercado de valores.16 Estas "habilidades" son paquetes de prompts y scripts que permiten realizar tareas de investigación avanzada:

* **Analista de Noticias de Mercado:** Utiliza herramientas de búsqueda web para analizar eventos de los últimos 10 días, enfocándose en decisiones de la FOMC, política de bancos centrales y eventos geopolíticos críticos.16
* **Analista de Rotación Sectorial:** Evalúa los patrones de ciclo de mercado (temprano, medio, tardío o recesión) basándose en la teoría de ciclos económicos, lo que permite ajustar la cartera según el contexto macro.16
* **Detección de Techos de Mercado:** Emplea indicadores técnicos y de sentimiento para identificar probabilidades de agotamiento en las tendencias alcistas.16

Estas herramientas demuestran que el uso de Claude en trading no se limita a la generación de código, sino que abarca la creación de un sistema de soporte de decisiones que integra la teoría económica con la realidad informativa actual.16

## **Gemini 1.5 Pro y el Análisis de Inteligencia Geopolítica**

Mientras que Claude destaca en la ejecución y el flujo de trabajo en terminal, Gemini 1.5 Pro se ha posicionado como una herramienta de investigación profunda gracias a su ventana de contexto de hasta 2 millones de tokens y su integración nativa con el ecosistema de Google.18

### **Gemini Deep Research y la Síntesis de Noticias Globales**

La funcionalidad Gemini Deep Research permite a los inversores realizar investigaciones autónomas que van mucho más allá de una simple consulta de chatbot.18 El agente construye un plan de investigación detallado, navega de forma independiente por la web buscando fuentes primarias y secundarias, y sintetiza los hallazgos en informes estructurados.18

En el ámbito geopolítico, Gemini ha sido utilizado para analizar transcripciones de noticias de televisión a escala planetaria mediante el proyecto GDELT.21 Se han documentado experiencias donde Gemini 3 Pro "observa" un día completo de transmisiones internacionales para generar reportes de inteligencia similares al "Daily Brief" presidencial, identificando narrativas de desinformación, cambios estratégicos en potencias regionales y la evolución de crisis humanitarias o militares.21 La capacidad del modelo para entrelazar las implicaciones domésticas de eventos internacionales permite a los traders anticipar movimientos en mercados de divisas o materias primas que dependen de la estabilidad política.21

### **Gemini Quant y la Estrategia de los Tres Pilares**

El repositorio gemini\_quant ofrece una extensión para la CLI de Gemini diseñada específicamente para el análisis de mercados.22 Su metodología se basa en una investigación rigurosa dividida en tres pilares fundamentales:

1. **Rendimiento Financiero:** Análisis de ingresos, márgenes y KPIs de reportes de ganancias.22
2. **Posicionamiento de Mercado:** Comparativa con pares de la industria y análisis competitivo.22
3. **Inteligencia Avanzada:** Integración de flujos de opciones (ratios put/call), señales de insiders (compras y ventas de ejecutivos) y contexto técnico de soportes y resistencias.22

Este framework permite realizar análisis detallados de mercados de predicción como Polymarket, donde el agente evalúa el valor esperado (EV) comparando las probabilidades implícitas en el mercado con datos del mundo real y el sentimiento de las noticias.22

## **Casos de Uso, Experiencias y Blogs de Implementación**

La teoría de los agentes inteligentes se materializa en experiencias documentadas por traders que han integrado estas herramientas en sus flujos diarios.

### **El Caso del Trader de Reddit y las "Trade Cards"**

Una de las experiencias más citadas en comunidades de inversión describe a un usuario que dedicó ocho meses a construir una plataforma de trading utilizando Claude.23 El sistema escanea diariamente 500 acciones del S\&P 500 y genera "tarjetas de operación" (trade cards) que incluyen:

* Métricas financieras en tiempo real y calificaciones de analistas.
* Historial de transacciones de insiders y resultados de ganancias.
* Sentimiento de los titulares de noticias recientes.
* Análisis de volatilidad implícita frente a la histórica para identificar ventajas en el precio de las opciones.23

Lo relevante de este caso es que Claude no toma las decisiones de compra, sino que actúa como un procesador de señales que traduce números densos en explicaciones en lenguaje natural sobre *por qué* una configuración específica es atractiva, permitiendo al trader humano mantener el control final mientras se beneficia de la capacidad de procesamiento de la IA.23

### **Comparativa de Rendimiento: Claude vs. Gemini vs. ChatGPT**

Un estudio longitudinal de 473 días comparó carteras gestionadas por Claude, Gemini y ChatGPT, proporcionándoles los mismos datos de mercado, presentaciones ante la SEC e indicadores económicos.24

| Modelo | Rendimiento vs. Mercado | Beta (Sensibilidad) | Máximo Drawdown |
| :---- | :---- | :---- | :---- |
| Claude | \+27.74% | 0.8 (Menos reactivo) | \-14% (Superior defensa) 24 |
| Gemini | \+13.04% | 0.9 (Sigue al mercado) | \-23% (Mayor riesgo) 24 |
| ChatGPT | \-3.34% | 0.6 (Desconectado) | \-18% (Medio) 24 |

Claude demostró una capacidad superior para tomar ganancias en sectores volátiles como los metales y rebalancear hacia carteras diversificadas en momentos de incertidumbre geopolítica.24 Gemini, por su parte, mostró una tendencia a concentrarse fuertemente en sectores de extracción de recursos (petróleo y oro), lo que incrementó su exposición a las oscilaciones de los precios de las materias primas influenciadas por el contexto internacional.24

### **QuantaAlpha y la Automatización de Factores con Claude Code**

En febrero de 2026, el investigador Saulius desarrolló QuantaAlpha, un framework de minería de factores autónomo utilizando Claude Code.17 Este sistema analizó una década de datos de 53 contratos de futuros de materias primas. El uso de Claude Haiku para el procesamiento de noticias resultó ser extremadamente eficiente, con un coste de aproximadamente $0.05 a $0.10 diarios para procesar cientos de ítems informativos, generando señales de sentimiento con niveles de confianza superiores al 65% para guiar las salidas de posiciones largas ante noticias bajistas.17

## **Integración Técnica: Scripts, Repositorios y Automatización**

Para los desarrolladores que buscan implementar estos sistemas, existen repositorios que ofrecen el código base necesario para conectar las noticias con la ejecución.

### **TradeAgent: Conectando Noticias con Alpaca y Supabase**

El repositorio enving/TradeAgent proporciona un sistema de trading autónomo que utiliza Claude 3.5 Sonnet para analizar más de 90 artículos por ticker.25 La lógica del sistema se divide en:

* **Análisis de Sentimiento:** Claude procesa noticias de Yahoo Finance y Finnhub, detectando puntos de inflexión y cambios de tendencia mediante regresión lineal.25
* **Estrategia de Momentum:** Integra indicadores como RSI y MACD, exigiendo que el sentimiento sea superior a 0.6 para confirmar las entradas.25
* **Infraestructura de Datos:** Todas las señales y los razonamientos detallados de la IA se almacenan en Supabase, lo que permite una auditoría completa de por qué se tomó cada decisión en función de las noticias disponibles en ese momento.25

### **Procesamiento de Newsletters con Gemini Flash**

Un enfoque más sencillo pero efectivo se encuentra en el repositorio kamilstanuch/automated-news-clipping-with-gemini.26 Este script de Google Apps utiliza la API de Gemini 1.5 Flash para extraer noticias de newsletters en Gmail y organizarlas en Google Sheets.26 El sistema categoriza las noticias por tema y valida la relevancia de los enlaces, permitiendo a un inversor tener un panel de control actualizado con los eventos geopolíticos y corporativos más importantes de su sector sin intervención manual.26

## **El Impacto del Contexto Geopolítico en la Toma de Decisiones**

La capacidad de los LLMs para cuantificar el riesgo geopolítico ha sido validada por investigaciones académicas que proponen el índice AI-GPR.27 A diferencia de los métodos tradicionales de conteo de palabras clave, los modelos de IA pueden distinguir cuándo un conflicto es el tema central de una noticia y cuándo es solo una mención periférica, asignando gradaciones de intensidad de riesgo.27

### **Digital War Room: Inteligencia OSINT para Traders**

El proyecto Digital War Room es una plataforma multi-agente que utiliza herramientas de inteligencia de fuentes abiertas (OSINT) para crear análisis geopolíticos.28 Bajo la supervisión de Claude Sonnet, el sistema despliega agentes especializados:

* **Agente DIPLO:** Monitorea señales diplomáticas y legales de la ONU y listas de sanciones.29
* **Agente ENERGY:** Supervisa infraestructuras críticas y el estrés en el transporte de materias primas, con monitores específicos para puntos de estrangulamiento como el Estrecho de Ormuz.29
* **Agente FININT:** Analiza cadenas de propiedad y el impacto de las sanciones financieras en tiempo real.29

Esta estructura permite a un inversor no solo saber "qué pasó", sino entender "qué significa" para el mercado energético o financiero, proporcionando una puntuación de escalada que puede ser utilizada como disparador para coberturas (hedging) en carteras de inversión.29

## **Consideraciones sobre Seguridad, Límites y Riesgos**

El uso de Claude Code y Gemini en entornos financieros no está exento de riesgos operativos y técnicos que deben ser gestionados con rigor profesional.

### **Vulnerabilidades y Fugas de Información**

Se han documentado incidentes de seguridad críticos, como la filtración accidental del código fuente completo de Claude Code en 2026, que permitió a investigadores y competidores analizar la lógica interna del sistema, incluyendo sus mecanismos de detección de frustración del usuario.30 Además, se han identificado vulnerabilidades de inyección de shell en la interfaz de línea de comandos de Claude, lo que subraya la importancia de utilizar claves de API con permisos restringidos y evitar la ejecución de comandos sin supervisión en entornos que contengan datos sensibles.31

### **Gestión de Contexto y Alucinaciones**

Un desafío persistente es la degradación del razonamiento cuando el contexto del chat se sobrecarga. Los expertos recomiendan la estrategia de "una tarea, una sesión" para mantener la precisión.10 Claude Code permite mitigar esto mediante el uso de archivos CLAUDE.md que actúan como memoria persistente del proyecto, donde se definen las convenciones de datos y el contexto del mercado, evitando que el modelo pierda el hilo de la estrategia durante sesiones largas.10

| Riesgo Operativo | Manifestación en Trading | Mitigación Recomendada |
| :---- | :---- | :---- |
| Alucinación de Cifras | Cálculo incorrecto de ratios de Sharpe o Sortino | Verificación mediante librerías de Python validadas (Pandas/NumPy) 17 |
| Sesgo Geopolítico | Mismatch entre entrenamiento y realidad actual | Uso de búsqueda web en tiempo real y múltiples modelos (Cross-check) 21 |
| Agotamiento de Límites | Pérdida de contexto a mitad de un análisis crítico | Uso de planes Pro/Max y estructuración de tareas breves 15 |
| Inyección de Prompts | Ejecución de órdenes no deseadas por noticias falsas | Implementación de humanos-en-el-bucle (Human-in-the-loop) 23 |

## **Conclusión y Perspectivas Futuras**

La integración de Claude Code y Gemini en el trading basado en noticias representa una transición desde el algoritmo reactivo hacia el agente proactivo. Los repositorios analizados, como TradingAgents y MarketSenseAI, demuestran que la inteligencia real en la inversión moderna surge de la colaboración entre múltiples agentes especializados que pueden debatir el impacto de una noticia geopolítica con la misma profundidad que un analista humano.3

La experiencia de los usuarios sugiere que estas herramientas son más efectivas cuando actúan como "multiplicadores de fuerza", procesando volúmenes masivos de información (noticias, SEC filings, redes sociales) para entregar señales digeribles y fundamentadas.23 A medida que los modelos evolucionan hacia capacidades proactivas y persistentes, como los proyectados modos "Kairos" de Anthropic, el trader del futuro será aquel capaz de orquestar estos ecosistemas de inteligencia para navegar la volatilidad de un mundo interconectado.30

#### **Fuentes citadas**

1. Large Language Model Agent in Financial Trading: A Survey \- arXiv, acceso: abril 7, 2026, [https://arxiv.org/html/2408.06361v2](https://arxiv.org/html/2408.06361v2)
2. TradingAgents: Multi-Agents LLM Financial Trading Framework \- arXiv, acceso: abril 7, 2026, [https://arxiv.org/html/2412.20138v5](https://arxiv.org/html/2412.20138v5)
3. TradingAgents: Multi-Agents LLM Financial Trading Framework, acceso: abril 7, 2026, [https://tradingagents-ai.github.io/](https://tradingagents-ai.github.io/)
4. MARAG-Fin: An Intelligent Multi-agent RAG-LLM Architecture Integrating Financial News Sentiment and Time Series Data for Data-driven Trading Decision-making \- Open Academic Journals Index, acceso: abril 7, 2026, [https://oaji.net/pdf.html?n=2025/3603-1768747789.pdf](https://oaji.net/pdf.html?n=2025/3603-1768747789.pdf)
5. TradingAgents: Multi-Agents LLM Financial Trading Framework \- GitHub, acceso: abril 7, 2026, [https://github.com/TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
6. weivea/tradingagents-marketplace: TradingAgents ... \- GitHub, acceso: abril 7, 2026, [https://github.com/weivea/tradingagents-marketplace](https://github.com/weivea/tradingagents-marketplace)
7. MarketSenseAI 2.0: Enhancing Stock Analysis through LLM Agents Part of this research was funded by European Union Commission through Project FAME with grant number 101092639\. \- arXiv, acceso: abril 7, 2026, [https://arxiv.org/html/2502.00415v2](https://arxiv.org/html/2502.00415v2)
8. MarketSenseAI performance of rank-based strategies \- ResearchGate, acceso: abril 7, 2026, [https://www.researchgate.net/figure/MarketSenseAI-performance-of-rank-based-strategies\_tbl5\_386554547](https://www.researchgate.net/figure/MarketSenseAI-performance-of-rank-based-strategies_tbl5_386554547)
9. Can Large Language Models Beat Wall Street? Unveiling the Potential of AI in Stock Selection \- arXiv, acceso: abril 7, 2026, [https://arxiv.org/html/2401.03737v1](https://arxiv.org/html/2401.03737v1)
10. Mastering Claude Code: From First Launch to 250 PRs a Month \- InPhroNeSys, acceso: abril 7, 2026, [https://inphronesys.com/?p=1252](https://inphronesys.com/?p=1252)
11. Connect Claude Code to tools via MCP, acceso: abril 7, 2026, [https://code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)
12. Best MCP Servers for Claude Code \- TrueFoundry, acceso: abril 7, 2026, [https://www.truefoundry.com/blog/best-mcp-servers-for-claude-code](https://www.truefoundry.com/blog/best-mcp-servers-for-claude-code)
13. MCP Server \- Financial Datasets, acceso: abril 7, 2026, [https://docs.financialdatasets.ai/mcp-server](https://docs.financialdatasets.ai/mcp-server)
14. MCP Server For Financial Data by EODHD, acceso: abril 7, 2026, [https://eodhd.com/financial-apis/mcp-server-for-financial-data-by-eodhd](https://eodhd.com/financial-apis/mcp-server-for-financial-data-by-eodhd)
15. Claude Code for Data Work: What Works, What Doesn't \- Medium, acceso: abril 7, 2026, [https://medium.com/@databytoufik/claude-code-for-data-work-what-works-what-doesnt-15857bae127d](https://medium.com/@databytoufik/claude-code-for-data-work-what-works-what-doesnt-15857bae127d)
16. tradermonty/claude-trading-skills: Claude Code skills for ... \- GitHub, acceso: abril 7, 2026, [https://github.com/tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills)
17. Leveraging AI Tools like Claude and ChatGPT in Algorithmic Trading \- QuantVPS, acceso: abril 7, 2026, [https://www.quantvps.com/blog/algorithmic-trading-with-llm](https://www.quantvps.com/blog/algorithmic-trading-with-llm)
18. How to Use Gemini Deep Research for Competitive Intelligence and Market Reports | MindStudio, acceso: abril 7, 2026, [https://www.mindstudio.ai/blog/gemini-deep-research-competitive-intelligence](https://www.mindstudio.ai/blog/gemini-deep-research-competitive-intelligence)
19. Claude vs. Gemini: How Do They Compare? \- DataCamp, acceso: abril 7, 2026, [https://www.datacamp.com/blog/claude-vs-gemini](https://www.datacamp.com/blog/claude-vs-gemini)
20. How to Use Gemini Deep Research for Stock Trading \- Prospero.ai, acceso: abril 7, 2026, [https://www.prospero.ai/resources-blog/how-to-use-gemini-deep-research-for-stock-trading](https://www.prospero.ai/resources-blog/how-to-use-gemini-deep-research-for-stock-trading)
21. Planetary-Scale Deep Reasoning: Having Gemini 3 Pro Improve Its ..., acceso: abril 7, 2026, [https://blog.gdeltproject.org/planetary-scale-deep-reasoning-having-gemini-3-pro-improve-its-own-prompt-for-our-global-trends-report-for-tv-news/](https://blog.gdeltproject.org/planetary-scale-deep-reasoning-having-gemini-3-pro-improve-its-own-prompt-for-our-global-trends-report-for-tv-news/)
22. lopushok9/gemini\_quant: Free, easy-to-use, AI-driven ... \- GitHub, acceso: abril 7, 2026, [https://github.com/lopushok9/gemini\_quant](https://github.com/lopushok9/gemini_quant)
23. I spent 8 months asking Claude dumb questions. Now it scans 500 stocks and hands me trade cards with actual suggested positions. Here's the full story, and EXACTLY how it works\! FINAL MAJOR UPDATE\!\!\! : r/SideProject \- Reddit, acceso: abril 7, 2026, [https://www.reddit.com/r/SideProject/comments/1r87qz8/i\_spent\_8\_months\_asking\_claude\_dumb\_questions\_now/](https://www.reddit.com/r/SideProject/comments/1r87qz8/i_spent_8_months_asking_claude_dumb_questions_now/)
24. We gave Claude, Gemini, and ChatGPT money and financial data to trade stocks/ETFs. In 473 days, Claude is beating the market by 27.74%, outperforming Gemini by 14.7% and ChatGPT by 31.08% \- Reddit, acceso: abril 7, 2026, [https://www.reddit.com/r/Anthropic/comments/1qyomze/we\_gave\_claude\_gemini\_and\_chatgpt\_money\_and/](https://www.reddit.com/r/Anthropic/comments/1qyomze/we_gave_claude_gemini_and_chatgpt_money_and/)
25. enving/TradeAgent: AI-Powered Algorithmic Trading ... \- GitHub, acceso: abril 7, 2026, [https://github.com/enving/TradeAgent](https://github.com/enving/TradeAgent)
26. Automate news extraction from your Gmail newsletters and organize them in Google Sheets using the Gemini API. \- GitHub, acceso: abril 7, 2026, [https://github.com/kamilstanuch/automated-news-clipping-with-gemini](https://github.com/kamilstanuch/automated-news-clipping-with-gemini)
27. The AI-GPR Index: Measuring Geopolitical Risk using Artificial Intelligence \- Matteo Iacoviello, acceso: abril 7, 2026, [https://www.matteoiacoviello.com/research\_files/AI\_GPR\_PAPER.pdf](https://www.matteoiacoviello.com/research_files/AI_GPR_PAPER.pdf)
28. geopolitical-risk · GitHub Topics, acceso: abril 7, 2026, [https://github.com/topics/geopolitical-risk](https://github.com/topics/geopolitical-risk)
29. lina767/digital-war-room: Multi-agent platform using OSINT ... \- GitHub, acceso: abril 7, 2026, [https://github.com/lina767/digital-war-room](https://github.com/lina767/digital-war-room)
30. Claude Code – Economist Writing Every Day, acceso: abril 7, 2026, [https://economistwritingeveryday.com/tag/claude-code/](https://economistwritingeveryday.com/tag/claude-code/)
31. Claude Code Leak \-\> Exploit? Researchers found 3 shell injection bugs in the leaked source — all using shell:true with unsanitized input : r/cybersecurity \- Reddit, acceso: abril 7, 2026, [https://www.reddit.com/r/cybersecurity/comments/1sbb5k7/claude\_code\_leak\_exploit\_researchers\_found\_3/](https://www.reddit.com/r/cybersecurity/comments/1sbb5k7/claude_code_leak_exploit_researchers_found_3/)
32. Top 8 Claude Skills for Finance and Quantitative Developers \- Snyk, acceso: abril 7, 2026, [https://snyk.io/articles/top-claude-skills-finance-quantitative-developers/](https://snyk.io/articles/top-claude-skills-finance-quantitative-developers/)
33. How you guys use Gemini/Claude/GPT in investment research? : r/ValueInvesting \- Reddit, acceso: abril 7, 2026, [https://www.reddit.com/r/ValueInvesting/comments/1pnvkm7/how\_you\_guys\_use\_geminiclaudegpt\_in\_investment/](https://www.reddit.com/r/ValueInvesting/comments/1pnvkm7/how_you_guys_use_geminiclaudegpt_in_investment/)
34. How to use Google's Gemini to research coins before you invest \- TradingView, acceso: abril 7, 2026, [https://www.tradingview.com/news/cointelegraph:fb44c33a9094b:0-how-to-use-google-s-gemini-to-research-coins-before-you-invest/](https://www.tradingview.com/news/cointelegraph:fb44c33a9094b:0-how-to-use-google-s-gemini-to-research-coins-before-you-invest/)
35. Ask HN: Why is my Claude experience so bad? What am I doing wrong? \- Hacker News, acceso: abril 7, 2026, [https://news.ycombinator.com/item?id=47000206](https://news.ycombinator.com/item?id=47000206)
36. anthropics/financial-services-plugins \- GitHub, acceso: abril 7, 2026, [https://github.com/anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins)
37. Claude Cowork Plugins: Complete Guide for Professionals, acceso: abril 7, 2026, [https://pasqualepillitteri.it/en/news/200/claude-cowork-plugins-complete-guide-professionals](https://pasqualepillitteri.it/en/news/200/claude-cowork-plugins-complete-guide-professionals)

Para desarrollar este MVP (Producto Mínimo Viable), lo ideal es una arquitectura **híbrida y modular** que aproveche las fortalezas específicas de cada modelo en el ecosistema de 2026\. Dado que ya tienes la API de Alpaca, el enfoque debe ser crear un "hilo conductor" que vaya desde la detección de una noticia macro hasta la ejecución de una orden.

Aquí tienes una propuesta paso a paso para tu primera iteración:

### **Paso 1: Definir la "Mesa de Inversión" (Arquitectura de Agentes)**

Para que no sea un simple script, implementaremos una versión simplificada del framework **TradingAgents**, que divide las tareas en roles especializados .

1. **Agente Analista Macro (Gemini 3 Flash):** Su trabajo es el "vuelo raso". Monitorea volúmenes masivos de noticias internacionales, conflictos y aranceles . Gemini 3 Flash es ideal aquí por su bajo coste ($0.50/1M tokens) y velocidad (3x más rápido que Pro), permitiendo procesar cientos de artículos diarios por pocos céntimos.
2. **Agente de Hipótesis (Gemini 3 Pro):** Toma los hallazgos del analista y busca correlaciones profundas. Es el que diría: *"El cierre del Estrecho de Ormuz impactará el precio del petróleo, pero también acelerará la inversión en Small Caps de Energía Nuclear en EE.UU."* .
3. **El "Dúo de Debate" (Claude Code \+ Z.ai GLM 5.1):** Aquí entra la inteligencia de ejecución. Un agente actúa como **Bull** (defensor de la compra) y otro como **Bear** (crítico de riesgos). **Z.ai GLM 5.1** es la elección lógica para este rol, ya que es actualmente el "campeón" en el benchmark **PredictionArena** de predicción financiera y manejo de tareas de largo aliento.
4. **Agente de Ejecución (Claude Code \+ Alpaca):** El operador final que traduce la decisión del "Board" en una orden de Paper Trading.

### **Paso 2: Configuración del "Radar" (Línea de Investigación)**

Tomando tu ejemplo de **"Small Caps de Energía Nuclear"**, la primera iteración se centraría en este flujo:

* **Fuentes de Datos:** Conectar Gemini 3 Flash a fuentes como **GDELT** (para conflictos y realidad geopolítica) y **SEC EDGAR** (para movimientos de insiders en tickers específicos).
* **Tickers Objetivo (Watchlist):** En 2026, los nombres clave para este MVP serían **Nano Nuclear Energy (NNE)**, **Oklo (OKLO)** y **NuScale Power (SMR)**.
* **Disparadores (Triggers):** Programar al analista para buscar eventos como:
  * Acuerdos de energía nuclear con *hyperscalers* (como el reciente trato de Meta con Oklo).
  * Declaraciones pro-nucleares en foros internacionales como Davos.
  * Hitos regulatorios o de transporte de combustible (como el proyecto HALEU de NNE).

### **Paso 3: Elaboración de la "Trade Card"**

En lugar de una orden directa, el sistema debe generar una **Trade Card** . Esto te permite supervisar el MVP antes de darle autonomía total. La tarjeta incluiría:

* **Señal de Sentimiento:** Puntuación de \-1 a \+1 basada en noticias recientes.
* **Contexto Geopolítico:** Por qué esta acción es un "refugio" o una oportunidad ante el contexto actual (ej. aranceles a componentes chinos que favorecen a proveedores locales).
* **Análisis Técnico Rápido:** Niveles de soporte/resistencia calculados por el agente.

### **Paso 4: Implementación Técnica (MVP 1.0)**

Para empezar hoy mismo con tu API de Alpaca, te sugiero este *stack* de herramientas:

1. **Gemini Deep Research:** Úsalo manualmente para generar el primer informe estructural sobre el sector nuclear. Pídele que cree un "Research Brief" detallado.
2. **Claude Code con MCP (Model Context Protocol):** Instala los servidores MCP de **Financial Datasets** o **EODHD** . Esto permite que Claude Code "vea" precios reales y noticias de Alpaca directamente en tu terminal.
3. **Script de Unión:** Crea un pequeño script en Python que use alpaca-py para el Paper Trading. Claude Code puede escribir y testear este script de forma autónoma preguntándole: *"Crea un script que compre 10 acciones de NNE si el sentimiento de noticias de las últimas 24h es superior a 0.7"*.

### **¿Qué modelo usar para qué?**

* **Gemini 3 Flash:** Para el **procesamiento masivo** de noticias. Es imbatible en coste/beneficio para leer miles de titulares.
* **Gemini 3 Pro:** Para **investigación profunda** y síntesis de reportes de 10-K o transcripciones de llamadas de ganancias.
* **Z.ai GLM 5.1:** Para el **razonamiento estratégico** y la decisión final de inversión, aprovechando su especialización en mercados financieros.
* **Claude Code:** Como el **orquestador y ejecutor** en tu terminal, gestionando el código, los archivos y la conexión con la API de Alpaca.

Para el desarrollo de tu MVP en el ecosistema de 2026, la decisión sobre el almacenamiento es crítica para la "auditabilidad" de tu IA. Aquí tienes la recomendación técnica basada en las tendencias actuales de trading algorítmico y sistemas agenticos:

### **1\. El veredicto: ¿Base de datos o Archivos Planos?**

Para un MVP de trading basado en noticias, **la recomendación es usar SQLite**. Se considera la solución "Goldilocks" (ni muy simple, ni muy compleja) por varias razones:

* **Zero Operational Overhead:** SQLite no es un servidor; es un archivo único en tu disco. No necesitas Docker ni configurar procesos adicionales, lo que encaja perfectamente con el flujo de trabajo de **Claude Code**.
* **Audit Trail (Rastro de Auditoría):** A diferencia de los archivos planos, SQLite te permite relacionar una noticia específica con una decisión de inversión y una orden de Alpaca de forma relacional. Esto es vital para preguntarle a Claude después: *"¿Por qué compraste NNE el martes pasado?"*.
* **Manejo de JSON:** En 2026, SQLite ha optimizado enormemente el tipo de dato **JSONB**, lo que te permite guardar las respuestas completas de los modelos (Gemini/Claude) directamente y consultarlas con SQL casi tan rápido como una base de datos vectorial.
* **Simplicidad para la IA:** Para Claude Code, es mucho más fácil ejecutar un comando sqlite3 trading.db "SELECT..." que parsear y filtrar manualmente 200 archivos JSON o CSV dispersos.

### **2\. Arquitectura del Stack MVP**

Tu "Mesa de Inversión" se puede construir con este stack minimalista pero potente:

* **Orquestador:** **Claude Code (CLI)**. Será tu "Terminal de Mando" donde correrás los scripts y gestionarás el código.
* **Cerebro de Investigación:** **Gemini 3 Flash** (vía API). Es el modelo más eficiente en coste ($0.001 por noticia) para procesar el flujo masivo de titulares y extraer sentimientos.
* **Cerebro de Decisión:** **Z.ai GLM 5.1** o **Gemini 3 Pro**. Úsalos solo cuando Gemini Flash detecte algo "caliente". Actuarán como el comité que valida la hipótesis.
* **Base de Datos:** **SQLite**. Para guardar:
  1. Titulares y resúmenes de noticias.
  2. Sentiment scores.
  3. Log de razonamiento (por qué se tomó la decisión).
  4. Estado de las órdenes de Alpaca.
* **Ejecución:** **Python \+ py-alpaca-api**. Esta librería simplifica la conexión con Alpaca para órdenes Paper Trading.

### **3\. Implementación del "Radar Nuclear" (Paso a Paso)**

Para tu línea de investigación sobre **Small Caps de Energía Nuclear**, puedes estructurar tus datos así:

1. **Watchlist Dinámica:** Define tickers como **NNE (Nano Nuclear Energy)**, **OKLO (Oklo Inc.)**, y **SMR (NuScale Power)**.
2. **Fuentes de Noticias (News Feed):** Alpaca tiene un endpoint de noticias, pero para el contexto geopolítico debes usar el **News API de Gemini** o conectarlo con el servidor MCP de **Financial Datasets**.
3. **El Flujo del MVP:**
   * **T+0:** Un script en Python pide noticias de las últimas 24h sobre "Nuclear SMR" y "Uranium supply".
   * **T+1:** Gemini Flash clasifica cada noticia: *Impacto (1-10), Sentimiento (-1 a 1\) y Relevancia Geopolítica*.
   * **T+2:** Si el sentimiento acumulado supera 0.7, Claude Code (vía script) consulta a Z.ai GLM 5.1 para validar la hipótesis: *"¿Es este un movimiento macro real o solo ruido?"*.
   * **T+3:** Se guarda la decisión en SQLite y se envía la orden de compra a Alpaca.

### **4\. Estructura de archivos sugerida**

Para empezar con Claude Code, crea esta estructura en tu carpeta de proyecto:

* CLAUDE.md: Configura aquí las reglas (ej: "Siempre usa SQLite", "Max 5% de capital por operación").
* trading.db: Tu base de datos SQLite.
* agents/: Carpeta con los prompts específicos para tu "Analista Nuclear" y tu "Gestor de Riesgos".
* scripts/: Scripts de Python para conectar Alpaca y los LLMs.

**¿Quieres que le pidamos a Claude Code que genere el esquema de la base de datos SQLite y el script básico de conexión con Alpaca para empezar?**

Para armar este MVP de forma robusta pero ágil, debemos definir primero la **cadencia** y el **estilo de inversión**, ya que eso determinará dónde vive el código y cuánto te costará operarlo.

Aquí tienes la hoja de ruta para tu primera iteración:

### **1\. Estrategia: ¿Day Trading o Swing Trading?**

Para un sistema basado en **noticias geopolíticas e infraestructura** (como la energía nuclear), el **Swing Trading** (posiciones de días o semanas) es mucho más propicio que el Day Trading.

* **¿Por qué?** El impacto de una noticia macro (ej. "Aranceles al uranio ruso" o "Aprobación de un SMR en Idaho") no se agota en 5 minutos; suele generar tendencias de varios días mientras el mercado "digiere" la noticia .
* **Frecuencia:** Para el MVP, **una vez al día (Pre-market)** o **dos veces (Apertura y Cierre)** es ideal. Un monitoreo permanente genera "ruido" y te haría gastar tokens innecesariamente en noticias irrelevantes.

### **2\. Infraestructura: ¿Local o VPS?**

* **Fase de Desarrollo (Semana 1-2):** Quédate en tu **PC Local**. Claude Code funciona mejor cuando tienes acceso directo a los archivos y puedes ver cómo interactúa con tu terminal .
* **Fase de Ejecución (MVP estable):** Pásalo a un **VPS** (como un QuantVPS o un servidor Linux básico). Esto garantiza que el "Radar" no se apague si tu PC entra en suspensión o pierde el Wi-Fi.

### **3\. El Stack Técnico del MVP (Arquitectura "Nuclear")**

Podemos estructurarlo de la siguiente manera, repartiendo el trabajo según la "inteligencia" de cada modelo:

| Capa | Herramienta / Modelo | Función |
| :---- | :---- | :---- |
| **Ingesta de Noticias** | **Gemini 3 Flash** | Lee el feed de Alpaca News y GDELT. Filtra lo que es "paja" y detecta eventos clave sobre uranio o reactores . |
| **Generador de Hipótesis** | **Gemini 3 Pro** | Elabora el análisis profundo: *"Si ha subido el precio del uranio un 5% y NNE acaba de firmar un acuerdo con la DOE, la probabilidad de subida es X"* . |
| **Comité de Inversión** | **Z.ai GLM 5.1** | Actúa como el analista senior que revisa la hipótesis. Es experto en razonamiento de largo alcance y tareas financieras complejas. |
| **Operador y Código** | **Claude Code** | Escribe los scripts de Python, gestiona la base de datos **SQLite** y ejecuta las órdenes en **Alpaca** . |

### **4\. Paso a Paso: Tu primera sesión de trabajo**

Para empezar hoy mismo, abre tu terminal en una carpeta nueva y sigue este orden:

#### **Paso A: Inicializar el entorno con Claude Code**

Corre /init en Claude Code para crear tu archivo CLAUDE.md. Define ahí que estás construyendo un sistema de trading para Alpaca enfocado en "Nuclear Small Caps" .

#### **Paso B: El "Radar Nuclear" (Base de Datos)**

Pide a Claude Code:

*"Crea un esquema de base de datos SQLite con tablas para: 1\. Noticia (titular, fuente, sentimiento), 2\. Hipótesis (texto, confianza), 3\. Tickers (SMR, OKLO, NNE, CCJ) y 4\. Operaciones (precio entrada, salida, resultado)"* .

#### **Paso C: El Script de Ingesta (Gemini \+ Alpaca)**

Crea un script en Python que:

1. Use tu API Key para bajar noticias de las últimas 24h de esos 4 tickers.
2. Envíe los titulares a **Gemini 3 Flash** para obtener un "Sentiment Score" (de \-1 a 1).
3. Guarde todo en la tabla Noticia.

#### **Paso D: El "Inversion Board" (La Lógica)**

Una vez tengas datos, usa a **Z.ai GLM 5.1** (vía Claude Code) para preguntarle:

*"Basado en estas 10 noticias que hemos recogido hoy sobre NNE y el contexto macro de la nueva ley de energía nuclear (SHANTI 2025), ¿deberíamos abrir una posición de Paper Trading? Genera un reporte de decisión"*.

### **¿Por qué este enfoque es el mejor?**

1. **Auditable:** Si pierdes dinero (en papel), puedes ir a tu SQLite y leer exactamente qué noticia y qué razonamiento de la IA causó la compra.
2. **Costo-eficiente:** Gemini 3 Flash procesa el volumen por casi $0, y solo usas los modelos caros (GLM 5.1 o Gemini Pro) cuando hay una oportunidad real confirmada.
3. **Modular:** Si mañana quieres cambiar el sector nuclear por "Minería en la Luna", solo cambias la lista de tickers y el prompt de investigación.

Exacto, **SQLite no se "instala" como un servidor** (tipo MySQL o PostgreSQL). Es simplemente un archivo que vive en la carpeta de tu proyecto. Sin embargo, para que tu código pueda leer ese archivo, sí necesitas instalar una **librería (driver)**.

Dependiendo de cómo configures tu bot con **Claude Code**, aquí tienes cómo se maneja:

### **1\. Si tu lógica de trading es en Python (Recomendado)**

Python ya trae SQLite incluido en su librería estándar, por lo que **no tienes que instalar nada** para empezar a usarlo. Solo pones import sqlite3 en tu script.

Sin embargo, para facilitarte la vida, podrías instalar herramientas adicionales mediante **pip**:

* pip install pandas: Para volcar datos de la BD a tablas de análisis rápidamente.
* pip install sqlalchemy: Si prefieres no escribir SQL puro y usar objetos.

### **2\. Si usas Node.js (El entorno de Claude Code)**

Si quieres que Claude ejecute scripts de Javascript directamente para manejar la BD, entonces usas **npm**:

* npm install sqlite3 o npm install better-sqlite3.
* Esto creará una carpeta node\_modules en tu proyecto, pero la base de datos seguirá siendo un simple archivo (ej. trading.db).

### **3\. ¿Cómo lo ve Claude Code?**

Para Claude Code, el archivo .db es como cualquier otro archivo de texto o código. La ventaja es que:

1. **Cero configuración:** No tienes que configurar puertos, usuarios ni contraseñas.
2. **Portabilidad:** Si mueves la carpeta de tu PC a un VPS, la base de datos se va con ella simplemente copiando el archivo.
3. **Visibilidad:** Puedes pedirle a Claude: *"Lee las últimas 5 filas de la tabla de noticias en trading.db y dime cuál tuvo el sentimiento más alto"*.

### **Resumen del proceso de "Instalación" para tu MVP:**

1. **Crea la carpeta** de tu proyecto.
2. **Inicializa el entorno:** Si usas Python, crea un entorno virtual (python \-m venv venv).
3. **Dile a Claude Code:** *"Genera un script de Python llamado init\_db.py que cree un archivo trading.db con las tablas para noticias y órdenes"*.
4. **Ejecuta el script:** Al correrlo, verás aparecer el archivo trading.db en tu carpeta. **¡Eso es todo\!**

Sí, lo vas a necesitar por dos razones fundamentales: **seguridad** y **conveniencia**.

En el contexto de un bot de trading, cuando hablamos de "env" solemos referirnos a dos cosas distintas que deberías configurar en tu carpeta de proyecto:

### **1\. El archivo .env (Para tus llaves secretas)**

Es un archivo de texto simple donde guardarás tus credenciales. Es **obligatorio** por seguridad; nunca debes escribir tus API Keys directamente en el código de Python o Javascript.

Para tu MVP, tu archivo .env debería verse así:

Bash

\# Alpaca Keys (Alpaca las detecta automáticamente si usas estos nombres)
APCA\_API\_KEY\_ID=tu\_api\_key\_de\_alpaca
APCA\_API\_SECRET\_KEY=tu\_secret\_key\_de\_alpaca
APCA\_API\_BASE\_URL=https://paper-api.alpaca.markets

\# LLM Keys
GEMINI\_API\_KEY=tu\_llave\_de\_google\_studio
ZAI\_API\_KEY=tu\_llave\_de\_z\_ai

* **Ventaja:** La librería de Alpaca está programada para buscar estas variables con esos nombres exactos (APCA\_API\_KEY\_ID, etc.) y conectarse sola sin que tengas que configurar nada más en el script.
* **Seguridad:** Debes añadir el nombre .env a un archivo llamado .gitignore para que, si subes tu código a GitHub, no publiques tus llaves por error.

### **2\. El "Virtual Env" o venv (Para tus librerías)**

Esto es un entorno aislado en tu PC para que las librerías de este proyecto (como alpaca-trade-api o google-genai) no se mezclen con otras que tengas instaladas.

Para crearlo, desde tu terminal en la carpeta del proyecto, corre:

1. python \-m venv venv (Crea el entorno).
2. source venv/bin/activate (En Mac/Linux) o venv\\Scripts\\activate (En Windows).

### **¿Cómo interactúa Claude Code con esto?**

Claude Code es muy inteligente gestionando esto:

* **Lectura:** Claude puede leer tu archivo .env para saber qué servicios tienes activos, pero no lo compartirá en sus respuestas si detecta que son llaves sensibles.
* **Configuración:** Puedes pedirle: *"Claude, instala las dependencias necesarias en mi entorno virtual y configura un script para verificar que las llaves del.env funcionan"*.
* **Persistencia:** Claude Code utiliza un archivo llamado CLAUDE.md como "memoria del proyecto" donde anotará que estás usando SQLite y Python, para no olvidarlo en la siguiente sesión.
