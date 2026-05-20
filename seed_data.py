import sys
import json
import urllib.request
import urllib.parse
from http.cookiejar import CookieJar

def seed_data(base_url):
    print(f"Starting data seed against {base_url}...")
    
    # Set up session with cookie jar so we stay logged in
    cookie_jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    urllib.request.install_opener(opener)

    # 1. Register a fake user
    print("\n--- Registering Demo User ---")
    register_data = urllib.parse.urlencode({
        'username': 'demo_user',
        'email': 'demo@example.com',
        'password': 'password123',
        'password_confirm': 'password123'
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(f"{base_url}/register", data=register_data)
        urllib.request.urlopen(req)
        print("Registration successful (or user already exists).")
    except Exception as e:
        print(f"Registration response: {e}")

    # 2. Login
    print("\n--- Logging In ---")
    login_data = urllib.parse.urlencode({
        'username': 'demo_user',
        'password': 'password123'
    }).encode('utf-8')
    
    try:
        req = urllib.request.Request(f"{base_url}/login", data=login_data)
        urllib.request.urlopen(req)
        print("Login successful.")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 3. Add Fake Papers (Triggers Prometheus 'app_papers_added_total')
    print("\n--- Adding Research Papers ---")
    papers = [
        {
            'title': 'Attention Is All You Need',
            'authors': 'Vaswani et al.',
            'publication': 'NIPS',
            'year': '2017',
            'doi': '10.48550/arXiv.1706.03762',
            'url': 'https://arxiv.org/abs/1706.03762',
            'abstract': 'We propose a new simple network architecture, the Transformer...',
            'keywords': 'AI, NLP, Transformer'
        },
        {
            'title': 'Deep Residual Learning for Image Recognition',
            'authors': 'He et al.',
            'publication': 'CVPR',
            'year': '2016',
            'doi': '10.1109/CVPR.2016.90',
            'url': 'https://arxiv.org/abs/1512.03385',
            'abstract': 'Deeper neural networks are more difficult to train...',
            'keywords': 'Computer Vision, ResNet, Deep Learning'
        },
        {
            'title': 'BERT: Pre-training of Deep Bidirectional Transformers',
            'authors': 'Devlin et al.',
            'publication': 'NAACL',
            'year': '2019',
            'doi': '10.48550/arXiv.1810.04805',
            'url': 'https://arxiv.org/abs/1810.04805',
            'abstract': 'We introduce a new language representation model called BERT...',
            'keywords': 'NLP, BERT, Transformers'
        }
    ]

    for paper in papers:
        paper_data = urllib.parse.urlencode(paper).encode('utf-8')
        try:
            req = urllib.request.Request(f"{base_url}/papers/add", data=paper_data)
            urllib.request.urlopen(req)
            print(f"Added paper: {paper['title']}")
        except Exception as e:
            print(f"Failed to add paper '{paper['title']}': {e}")

    # 4. Trigger AI Chat (Triggers Prometheus 'app_ai_chat_requests_total')
    print("\n--- Sending AI Chat Requests ---")
    chat_messages = [
        "Can you summarize the Transformer architecture?",
        "What is the difference between BERT and GPT?",
        "Suggest some next milestones for my NLP research."
    ]

    for msg in chat_messages:
        chat_data = json.dumps({'message': msg}).encode('utf-8')
        try:
            req = urllib.request.Request(f"{base_url}/chat", data=chat_data, headers={'Content-Type': 'application/json'})
            response = urllib.request.urlopen(req)
            response_json = json.loads(response.read().decode('utf-8'))
            print(f"Sent: '{msg}'")
            print(f"AI Responded: '{response_json.get('response', '')[:50]}...'")
        except Exception as e:
            print(f"Chat failed: {e}")

    print("\nData seeding complete! Check your Grafana dashboard, the metrics should be spiking right now!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python seed_data.py <BASE_URL>")
        print("Example: python seed_data.py http://13.235.17.74")
        sys.exit(1)
        
    base_url = sys.argv[1].rstrip('/')
    seed_data(base_url)
