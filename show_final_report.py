def show_final_report():
    """Display the final security report"""
    try:
        with open('final_security_report.md', 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"Error reading report: {e}")

if __name__ == "__main__":
    show_final_report()