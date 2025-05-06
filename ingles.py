import sys

# Lista de verbos con sus formas
verbs = [
    ("be", "was /were", "been"),
    ("become", "became", "become"),
    ("begin", "began", "begun"),
    ("bleed", "bled", "bled"),
    ("break", "broke", "broken"),
    ("bring", "brought", "brought"),
    ("build", "built", "built"),
    ("burn", "burnt", "burnt"),
    ("buy", "bought", "bought"),
    ("cast", "cast", "cast"),
    ("catch", "caught", "caught"),
    ("choose", "chose", "chosen"),
    ("come", "came", "come"),
    ("cost", "cost", "cost"),
    ("cut", "cut", "cut"),
    ("do", "did", "done"),
    ("draw", "drew", "drawn"),
    ("dream", "dreamt", "dreamt"),
    ("drink", "drank", "drunk"),
    ("drive", "drove", "driven"),
    ("eat", "ate", "eaten"),
    ("fall", "fell", "fallen"),
    ("feel", "felt", "felt"),
    ("fight", "fought", "fought"),
    ("find", "found", "found"),
    ("fly", "flew", "flown"),
    ("forbid", "forbade", "forbidden"),
    ("forget", "forgot", "forgotten"),
    ("forgive", "forgave", "forgiven"),
    ("get", "got", "gotten"),
    ("give", "gave", "given"),
    ("go", "went", "gone"),
    ("grow", "grew", "grown"),
    ("have", "had", "had"),
    ("hear", "heard", "heard"),
    ("hide", "hid", "hidden"),
    ("hit", "hit", "hit"),
    ("hold", "held", "held"),
    ("hurt", "hurt", "hurt"),
    ("keep", "kept", "kept"),
    ("know", "knew", "known"),
    ("learn", "learnt", "learnt"),
    ("leave", "left", "left"),
    ("let", "let", "let"),
    ("lie", "lay", "lain"),
    ("lose", "lost", "lost"),
    ("make", "made", "made"),
    ("mean", "meant", "meant"),
    ("meet", "met", "met"),
    ("pay", "paid", "paid"),
    ("put", "put", "put"),
    ("read", "read", "read"),
    ("ride", "rode", "ridden"),
    ("run", "ran", "run"),
    ("say", "said", "said"),
    ("see", "saw", "seen"),
    ("sell", "sold", "sold"),
    ("send", "sent", "sent"),
    ("show", "showed", "shown"),
    ("sing", "sang", "sung"),
    ("sleep", "slept", "slept"),
    ("speak", "spoke", "spoken"),
    ("spell", "spelt", "spelt"),
    ("stand", "stood", "stood"),
    ("steal", "stole", "stolen"),
    ("swim", "swam", "swum"),
    ("take", "took", "taken"),
    ("teach", "taught", "taught"),
    ("tell", "told", "told"),
    ("think", "thought", "thought"),
    ("throw", "threw", "thrown"),
    ("wake", "woke", "woken"),
    ("wear", "wore", "worn"),
    ("win", "won", "won"),
    ("write", "wrote", "written"),
]

# Dividir los verbos en niveles de 10
def dividir_en_niveles(verbs, nivel_size=10):
    return [verbs[i:i+nivel_size] for i in range(0, len(verbs), nivel_size)]

niveles = dividir_en_niveles(verbs)

def mostrar_menu():
    print("\n--- MENU DE NIVELES ---")
    for i in range(len(niveles)):
        print(f"{i+1}. Nivel {i+1}")
    print("0. Salir")

def jugar_nivel(nivel):
    if nivel < 1 or nivel > len(niveles):
        print("Nivel inválido.")
        return
    print(f"\n--- JUGANDO NIVEL {nivel} ---")
    errores = 0
    for verbo in niveles[nivel-1]:
        print(f"\nVerbo en infinitivo: {verbo[0]}")
        respuesta_simple = input("Simple Past: ").strip().lower()
        respuesta_participle = input("Past Participle: ").strip().lower()

        correcto_simple = verbo[1].lower().replace(" ", "")
        correcto_participle = verbo[2].lower().replace(" ", "")

        if respuesta_simple.replace(" ", "") == correcto_simple and respuesta_participle.replace(" ", "") == correcto_participle:
            print("✅ ¡Correcto!")
        else:
            print(f"❌ Incorrecto. Correcto sería: {verbo[1]} / {verbo[2]}")
            errores += 1
    print(f"\nNivel {nivel} terminado. Errores: {errores}")

def main():
    while True:
        mostrar_menu()
        try:
            opcion = int(input("Seleccione el nivel (0 para salir): "))
            if opcion == 0:
                print("¡Hasta luego!")
                sys.exit()
            jugar_nivel(opcion)
        except ValueError:
            print("❗ Error: Debe ingresar un número.")

if __name__ == "__main__":
    main()
