import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        return False
    return True

def check_camera():
    """Check if camera is available"""
    print("Checking camera availability...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("Camera is available!")
            cap.release()
            return True
        else:
            print("Camera is not available or not accessible.")
            return False
    except ImportError:
        print("OpenCV not installed.")
        return False

def run_application():
    """Run the main application"""
    print("Starting Real-Time Object Detection application...")
    try:
        import enhanced_app
        enhanced_app.main()
    except ImportError as e:
        print(f"Error importing application: {e}")
        print("Make sure all dependencies are installed.")
    except Exception as e:
        print(f"Error running application: {e}")

def main():
    print("Real-Time Object Detection Setup")
    print("=" * 40)
    
    # Check if requirements file exists
    if not os.path.exists("requirements.txt"):
        print("requirements.txt not found!")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Check camera
    if not check_camera():
        print("Warning: Camera not available. The application may not work properly.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Run application
    run_application()

if __name__ == "__main__":
    main()
