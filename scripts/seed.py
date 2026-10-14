import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to enable app imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models import User, ResearchPaper, Patent, Note, Reminder

def seed_database():
    app = create_app('development')
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Clear existing demo data
        db.session.query(Reminder).delete()
        db.session.query(Note).delete()
        db.session.query(Patent).delete()
        db.session.query(ResearchPaper).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        print("Seeding Users...")
        # Demo Admin: admin / admin123
        admin = User(username='admin', email='admin@researcher.org', role='admin')
        admin.set_password('admin123')
        
        # Demo Researcher: researcher / researcher123
        researcher = User(username='researcher', email='researcher@lab.org', role='researcher')
        researcher.set_password('researcher123')
        
        db.session.add(admin)
        db.session.add(researcher)
        db.session.commit()
        
        print("Seeding Research Papers for Researcher...")
        paper1 = ResearchPaper(
            user_id=researcher.id,
            title='Deep Residual Learning for Image Recognition',
            authors='He, K., Zhang, X., Ren, S., Sun, J.',
            journal='IEEE Conference on Computer Vision and Pattern Recognition (CVPR)',
            publication_year=2016,
            doi='10.1109/CVPR.2016.90',
            url='https://arxiv.org/abs/1512.03385',
            keywords='Deep Learning, Neural Networks, Computer Vision, ResNet',
            abstract=('Deeper neural networks are more difficult to train. We present a residual learning '
                      'framework to ease the training of networks that are substantially deeper than those '
                      'previously used. We explicitly reformulate the layers as learning residual functions '
                      'with reference to the layer inputs.'),
            status='Completed'
        )
        
        paper2 = ResearchPaper(
            user_id=researcher.id,
            title='Attention Is All You Need',
            authors='Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., Polosukhin, I.',
            journal='Advances in Neural Information Processing Systems (NeurIPS)',
            publication_year=2017,
            doi='10.48550/arXiv.1706.03762',
            url='https://arxiv.org/abs/1706.03762',
            keywords='Transformer, Attention Mechanism, Natural Language Processing, Deep Learning',
            abstract=('The dominant sequence transduction models are based on complex recurrent or convolutional '
                      'neural networks in an encoder-decoder configuration. We propose the Transformer, a model '
                      'architecture eschewing recurrence and relying entirely on an attention mechanism to draw '
                      'global dependencies between input and output.'),
            status='Reading'
        )
        
        paper3 = ResearchPaper(
            user_id=researcher.id,
            title='BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
            authors='Devlin, J., Chang, M. W., Lee, K., Toutanova, K.',
            journal='NAACL-HLT',
            publication_year=2019,
            doi='10.18653/v1/N19-1423',
            url='https://arxiv.org/abs/1810.04805',
            keywords='BERT, NLP, Transformers, Language Models',
            abstract=('We introduce a new language representation model called BERT, which stands for Bidirectional '
                      'Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional '
                      'representations from unlabeled text by jointly conditioning on both left and right context.'),
            status='Unread'
        )
        
        db.session.add_all([paper1, paper2, paper3])
        db.session.commit()
        
        print("Seeding Patents for Researcher...")
        patent1 = Patent(
            user_id=researcher.id,
            title='Quantum Neural Network Circuit Architecture and Error Correction System',
            patent_number='US 11,450,982 B2',
            description=('A quantum processing unit utilizing superconducting qubits configured for hybrid quantum-classical '
                         'neural network optimization and active fault-tolerant error mitigation.'),
            filing_date=datetime.strptime('2021-03-15', '%Y-%m-%d').date(),
            publication_date=datetime.strptime('2022-09-20', '%Y-%m-%d').date(),
            url='https://patents.google.com/patent/US11450982B2/en'
        )
        
        patent2 = Patent(
            user_id=researcher.id,
            title='Distributed Edge Tensor Processing Unit for Autonomous Driving',
            patent_number='US 10,987,654 B1',
            description=('System and method for real-time edge tensor compilation and low-latency inference on distributed vehicle sensors.'),
            filing_date=datetime.strptime('2020-01-10', '%Y-%m-%d').date(),
            publication_date=datetime.strptime('2021-04-05', '%Y-%m-%d').date(),
            url='https://patents.google.com/patent/US10987654B1/en'
        )
        
        db.session.add_all([patent1, patent2])
        db.session.commit()
        
        print("Seeding Notes...")
        note1 = Note(
            user_id=researcher.id,
            paper_id=paper1.id,
            content='ResNet-50 shortcut connections effectively solve vanishing gradient in deep architectures.'
        )
        note2 = Note(
            user_id=researcher.id,
            patent_id=patent1.id,
            content='Review claim 4 regarding quantum error mitigation thresholds against external hardware benchmarks.'
        )
        note3 = Note(
            user_id=researcher.id,
            content='General research goal for Q3: Benchmark Transformer self-attention efficiency vs linear attention models.'
        )
        
        db.session.add_all([note1, note2, note3])
        db.session.commit()
        
        print("Seeding Reminders...")
        reminder1 = Reminder(
            user_id=researcher.id,
            title='Submit NeurIPS Paper Camera-Ready Draft',
            description='Check double-blind formatting requirements and appendix proofs.',
            reminder_date=datetime.utcnow() + timedelta(days=7),
            completed=False
        )
        reminder2 = Reminder(
            user_id=researcher.id,
            title='Patent Renewal Fee Payment',
            description='Pay USPTO maintenance fee for US 10,987,654 B1.',
            reminder_date=datetime.utcnow() + timedelta(days=14),
            completed=False
        )
        reminder3 = Reminder(
            user_id=researcher.id,
            title='Lab Meeting Presentation',
            description='Present literature survey on Transformer models.',
            reminder_date=datetime.utcnow() - timedelta(days=2),
            completed=True
        )
        
        db.session.add_all([reminder1, reminder2, reminder3])
        db.session.commit()
        
        print("\nSeed Data Successfully Inserted!")
        print("----------------------------------------")
        print("Credentials for Testing:")
        print("  Admin User:      admin / admin123")
        print("  Researcher User: researcher / researcher123")
        print("----------------------------------------")

if __name__ == '__main__':
    seed_database()
