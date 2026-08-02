"""Punkt wejścia dla PyInstallera.

PyInstaller uruchamia wskazany plik jako skrypt najwyższego poziomu, a nie
jako moduł wewnątrz pakietu — więc importy względne w `ghostposter/gui.py`
(`from .blank import ...` itd.) by się wywaliły, gdyby to jego wskazać
bezpośrednio jako punkt wejścia. Ten plik jest cienką nakładką importującą
`ghostposter` jako normalny, zainstalowany pakiet, dzięki czemu importy
względne w środku działają tak samo jak przy `ghostposter-gui`.
"""

from ghostposter.gui import main

if __name__ == "__main__":
    main()
