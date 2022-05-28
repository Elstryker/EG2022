from bs4 import BeautifulSoup

def generateErrorTag(text, errorMessage="Erro na variável"):
    retStr = '<div class="error">'
    retStr += text
    retStr += f'<span class="errortext">{errorMessage}</span></div>'

    return retStr

def generateSubTag(text,subMessage="If conjugado"):
    retStr = '<div class="sub">'
    retStr += text
    retStr += f'<span class="subtext">{subMessage}</span></div>'
    return retStr



def generatePClassCodeTag(text):
    retStr = f'''
<p class="code">
    {text}
</p>'''

    return retStr

def generateHTMLStatReport(numDeclaredVars,errors,warnings,numInstructions):
    html = f'''<h1>Code Statistical Report</h1>
    <h2>Número de variáveis declaradas</h2>
    <ul>
        <li>Atómicas: {numDeclaredVars['atomic']}</li>
        <li>Conjuntos: {numDeclaredVars['set']}</li>
        <li>Listas: {numDeclaredVars['list']}</li>
        <li>Tuplos: {numDeclaredVars['tuple']}</li>
        <li>Dicionários: {numDeclaredVars['dict']}</li>
        <li>Total: {numDeclaredVars['atomic'] + numDeclaredVars['set'] + numDeclaredVars['list'] + numDeclaredVars['tuple'] + numDeclaredVars['dict']}</li>
    </ul>
    <br>
    <h2>Número de Instruções</h2>
    <ul>
        <li>Atribuições: {numInstructions['atribution']}</li>
        <li>Leituras: {numInstructions['read']}</li>
        <li>Escritas: {numInstructions['write']}</li>
        <li>Condicionais: {numInstructions['condition']}</li>
        <li>Cíclicas: {numInstructions['cycle']}</li>
        <li>Controlo Aninhadas: {numInstructions['nestedControl']}</li>
        <li>Total: {numInstructions['atribution'] + numInstructions['read'] + numInstructions['write'] + numInstructions['condition'] + numInstructions['cycle']}</li>
    </ul>
    <br>
    <h2>Erros</h2>
    <ul>'''

    for error in errors:
        html += f'''
        <li>{error}</li>'''

    html += '''
    </ul>
    <br>
    <h2>Warnings</h2>
    <ul>'''

    for warning in warnings:
        html += f'''
        <li>{warning}</li>'''

    html += '''
    </ul>'''

    return html



    

def generateCSS():
    retStr = '''
<style>
    .error {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
        color: red;
    }
    
    .code {
        position: relative;
        display: inline-block;
    }
    
    .error .errortext {
        visibility: hidden;
        width: 500px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px 0;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -40px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .error .errortext:after {
        content: "";
        position: absolute;
        top: 100%;
        left: 8%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #555 transparent transparent transparent;
    }
    
    .error:hover .errortext {
        visibility: visible;
        opacity: 1;
    }


    .sub {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black;
        color: green;
    }
    
    .sub .subtext {
        visibility: hidden;
        width: 500px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px 0;
        position: absolute;
        z-index: 1;
        bottom: 300%;
        left: 50%;
        margin-left: -40px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .sub .subtext:after {
        content: "";
        position: absolute;
        top: 100%;
        left: 8%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #555 transparent transparent transparent;
    }
    
    .sub:hover .subtext {
        visibility: visible;
        opacity: 1;
    }
</style>'''

    return retStr

def generateHTML(body,report):

    html = '''<!DOCTYPE html>
<html>'''

    html += generateCSS()

    html += '''

<body>

    <h2> Análise de código </h2>
    
    <pre><code>'''

    html += body

    html += '''

    </code></pre>'''

    html += report

    html += '''
</body>

</html>'''

    with open("index.html","w",encoding="utf-8") as f:
        f.write(html)

    return None

def insertGraphsHTML(html,nodes,edges):
    soup = BeautifulSoup(open('index.html'), 'html.parser')
    tagCFG =soup.new_tag("h1")
    tagCFG.string = "Control Flow Graph"
    soup.body.append(tagCFG)
    imgCFG = soup.new_tag("img",src="Control Flow Graph.gv.png")
    soup.body.append(imgCFG)
    tagComp =soup.new_tag("p")
    complexidade = edges-nodes+2
    tagComp.string = "Complexidade de McCabe<=>"+str(edges)+"-"+str(nodes)+"+2="+str(complexidade)
    soup.body.append(tagComp)
    tagSDG =soup.new_tag("h1")
    tagSDG.string = "System Dependency Graph"
    soup.body.append(tagSDG)
    imgSDG = soup.new_tag("img",src="System Dependency Graph.gv.png")
    soup.body.append(imgSDG)
    
    with open("index.html", "w") as file:
        file.write(str(soup))
        
