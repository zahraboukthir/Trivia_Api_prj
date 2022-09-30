import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from settings import DB_TEST_NAME, DB_USER, DB_PASSWORD
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        
        self.database_path ="postgresql://{}:{}@{}/{}".format(
               DB_USER, DB_PASSWORD, 'localhost:5432', DB_TEST_NAME)
        setup_db(self.app, self.database_path)
 
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # test ctg
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_404_category(self):
        res = self.client().get('/api/categories/9865')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")
    # test qts
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_404_sent_duestions(self):
        res = self.client().get('/questions?page=96586')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "resource not found")
#  test del qst
    def test_delete_question(self):
        res = self.client().delete('/questions/12')
        data = json.loads(res.data)
        print(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/968624')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


#  test cr qst
    def test_post_qst(self):
        new_question={
            "question":" what did you learn?",
            "answer" : " Flask Api ",
            "difficulty":2,
            "category":1
        }    
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        # self.assertGreater(len(Question.query.all()) ,
        #     len( Question.query.all()
        # )
        #     )
        self.assertTrue(data['success'])
        self.assertIn('new_question', data)
        self.assertIn('total_questions', data)

    def test_422_post_qst(self):
        new_question={
            "question":" what did you learn?",
            "answer" : " Flask Api ",
            "difficulty":2,
            "category":9
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], "unprocessable ressource")

#  test search qst
    def test_search_questions(self):
        new_search = {'searchTerm': 'new srch'}
        res = self.client().post('/questions/search', json=new_search)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])

    def test_search_not_found(self):
        request_data = {
            'searchTerm': None,
        }
        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
# test qst/ctg
    def test_qt_ctg(self):
        res = self.client().get('/categories/5/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Entertainment')

    def test_422_qt_ctg(self):
        res = self.client().get('/categories/8/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
#  test plquizz
    def testquiz(self):
        request_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }

        # make request and process response
        response = self.client().post('/quizzes', json=request_data)
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        # Ensures previous questions are not returned
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)

        # Ensures returned question is in the correct category
        self.assertEqual(data['question']['category'], 4)

    def test_400_play_quiz(self):
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()