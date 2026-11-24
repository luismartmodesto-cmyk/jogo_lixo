# Missão: Lixo no lugar certo

Jogo educativo em Python e Pygame para crianças de 6 a 10 anos. O menu explica a brincadeira em três passos; depois, arraste cada resíduo até a categoria correspondente, receba uma explicação curta e avance por duas etapas.

As cores e as orientações são referências gerais. A coleta seletiva e as regras de descarte variam entre municípios; confirme as instruções locais.

## Executar no computador

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Use o mouse ou toque para arrastar os itens. A interface se adapta a telas grandes, retrato e paisagem. Também é possível usar Enter ou Espaço para iniciar e avançar depois de uma resposta correta.

## Preparar para o navegador

Instale as dependências e gere a versão web com:

```powershell
python -m pip install -r requirements.txt
python scripts\build_web.py
```

A saída fica em `build\web`. O build usa uma cópia temporária com nome ASCII, corrige a referência de `BrowserFS` do template Pygbag e inclui essa biblioteca localmente.

Para testar a saída no computador:

```powershell
python -m http.server 8000 --directory build\web
```

Abra `http://localhost:8000`. O runtime Python e WebAssembly do Pygbag ainda é carregado de um CDN, então a primeira execução precisa de conexão com a internet.

## Testes

```powershell
python -m unittest discover -s tests
```

Os desenhos são feitos com formas do Pygame; o jogo não depende de imagens ou fontes externas.
