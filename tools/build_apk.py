import os
import sys
import shutil
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from web.build_dashboard import build_standalone_dashboard

def build_apk():
    android_dir = os.path.join(root_dir, "android")
    dist_dir = os.path.join(root_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)

    print("\n[APK Builder] 1. Compilazione e allineamento Dashboard Web HTML...")
    build_standalone_dashboard()

    print("\n[APK Builder] 2. Compilazione APK Android tramite Gradle...")
    gradlew_bat = os.path.join(android_dir, "gradlew.bat")
    cmd = [gradlew_bat, "assembleDebug"]

    res = subprocess.run(cmd, cwd=android_dir)
    if res.returncode != 0:
        print("[APK Builder] [ERRORE] Compilazione Gradle non riuscita.")
        return None

    src_apk = os.path.join(android_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
    dst_apk = os.path.join(dist_dir, "FantaMasterAI.apk")

    if os.path.exists(src_apk):
        shutil.copyfile(src_apk, dst_apk)
        size_mb = os.path.getsize(dst_apk) / (1024 * 1024)
        print("\n" + "="*65)
        print(">>> APK ANDROID COMPILATO CON SUCCESSO! <<<")
        print("="*65)
        print(f"File APK generato: {dst_apk}")
        print(f"Dimensione:        {size_mb:.2f} MB")
        print("Come installarlo sullo smartphone:")
        print("  1. Copia 'dist/FantaMasterAI.apk' sul telefono (USB, Telegram, Drive)")
        print("  2. Apri il file dal telefono e tocca 'Installa'")
        print("  3. Oppure esegui: adb install dist/FantaMasterAI.apk")
        print("="*65 + "\n")
        return dst_apk
    else:
        print(f"[APK Builder] [ERRORE] File APK non trovato in: {src_apk}")
        return None

if __name__ == "__main__":
    build_apk()
