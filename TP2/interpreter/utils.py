
def generateErrorTag(text, errorMessage="Erro na variável"):
    retStr = '<div class="error">'
    retStr += text
    retStr += f'<span class="errortext">${errorMessage}</span></div>'

    return retStr

def generateSubTag(text,subMessage="IF conjugado"):
    retStr = '<div class="sub">'
    retStr += text
    retStr += f'<span class="subtext">${subMessage}</span></div>'
    return retStr



def generatePClassCodeTag(text):
    retStr = f'''
<p class="code">
    {text}
</p>'''

    return retStr

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
        left: 20%;
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
        bottom: 125%;
        left: 50%;
        margin-left: -40px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .sub .subtext:after {
        content: "";
        position: absolute;
        top: 100%;
        left: 20%;
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

def generateHTML(body):

    html = '''<!DOCTYPE html>
<html>'''

    html += generateCSS()

    html += '''

<body>

    <h2> Análise de código </h2>
    
    <pre><code>'''

    html += body

    html += '''

</code></pre>
</body>

</html>'''

    with open("index.html","w",encoding="utf-8") as f:
        f.write(html)

    return None