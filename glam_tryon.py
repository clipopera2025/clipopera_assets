import os

GLAM_API_KEY = "BkhUMHs-bSJRtW9VSROlsw"


def main():
    glb_files = [f for f in os.listdir('.') if f.endswith('.glb')]
    print("Found GLB files:", glb_files)
    print("Using GLAM API key:", GLAM_API_KEY)
    print("This is a placeholder for the real GLAM try-on logic.")


if __name__ == "__main__":
    main()
