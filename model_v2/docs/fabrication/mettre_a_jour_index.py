#!/usr/bin/env python3
"""mettre_a_jour_index.py : ouvre le .docx dans LibreOffice (sans interface), met a jour
le sommaire et les listes, enregistre le .docx mis a jour et exporte le PDF.

Usage : python3 mettre_a_jour_index.py memoire.docx
Necessite LibreOffice (module python3-uno).
"""
import sys, os, subprocess, time
import uno
from com.sun.star.beans import PropertyValue

def prop(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p

def main():
    src = os.path.abspath(sys.argv[1])
    base = os.path.splitext(src)[0]
    port = 2002
    proc = subprocess.Popen(["soffice", "--headless", "--invisible", "--norestore",
                             f"--accept=socket,host=localhost,port={port};urp;"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ctx = None
    local = uno.getComponentContext()
    resolver = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
    for _ in range(60):
        try:
            ctx = resolver.resolve(f"uno:socket,host=localhost,port={port};urp;StarOffice.ComponentContext"); break
        except Exception:
            time.sleep(1)
    desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desk.loadComponentFromURL(uno.systemPathToFileUrl(src), "_blank", 0, (prop("Hidden", True),))
    for _ in range(2):  # deux passes : les numeros de page bougent quand le sommaire se remplit
        idx = doc.getDocumentIndexes()
        for i in range(idx.getCount()):
            idx.getByIndex(i).update()
        doc.refresh()
    print("index mis a jour :", doc.getDocumentIndexes().getCount())
    doc.storeToURL(uno.systemPathToFileUrl(base + ".docx"), (prop("FilterName", "MS Word 2007 XML"),))
    doc.storeToURL(uno.systemPathToFileUrl(base + ".pdf"), (prop("FilterName", "writer_pdf_Export"),))
    doc.close(True)
    try: desk.terminate()
    except Exception: pass
    proc.wait(timeout=60)
    print("ecrit", base + ".docx", "et", base + ".pdf")

if __name__ == "__main__":
    main()
