import sys, random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category
"""
setup_db(app)
   Create an endpoint to handle GET requests
    for questions, including pagination (every 10 questions). 
    This endpoint should return a list of questions, number of total questions, current category, categories.
"""
QUESTIONS_PER_PAGE = 10
def questions_pagination(request, selection):
    """
    to paginate questions (10 questions per page)
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    return questions[start:end]

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def GatAllCategories():
        try:
            categories = {}
            for category in Category.query.all():
                categories[category.id] = category.type
            return jsonify({
                'success': True,
                'categories':categories
            }), 200
        except Exception:
            abort(500)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def GetAllQuestions():
        touslesQuestions = Question.query.order_by(Question.id).all()
        
        questionsparpage = questions_pagination(request,touslesQuestions)

        touscategories = Category.query.order_by(Category.type).all()

        if len(questionsparpage) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': questionsparpage,
            'total_questions': len(touslesQuestions),
            'categories': {ctg.id: ctg.type for ctg in touscategories}
        })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def DeleteOneQuestion(question_id):
        deletedquestion = Question.query.filter(Question.id == question_id).one_or_none()
           
        if deletedquestion is None:
             abort(404)
        try:
             deletedquestion.delete()
             return jsonify({
                'success':True,
                'deleted':question_id,
                'total_questions': len( Question.query.order_by(Question.id).all())
                          })
        except:
              
              abort(404)
        
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def AddNewQuestion():
        try:
            body = request.get_json()
            qst = body.get("question", None)
            ans = body.get("answer", None)
            ctg = body.get("category", None)
            diff = body.get("difficulty", None)
            if qst is None or ans is None or diff is None or ctg is None:
                abort(422)
            else:
                question = Question(question=qst, answer=ans,
                                difficulty=diff,
                                category=ctg)
                question.insert()
                return jsonify({
                'success': True,
                'new_question_id': question.id,
                'new_question': question.question,
                'total_questions': len(Question.query.all()),
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @ app.route('/questions/search', methods=['POST'])
    def searchQuestions():
        search_term = request.get_json().get('searchTerm', None)
        try:
            if search_term is not None:
                selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            else:
                abort(404)
            paginated_questions = questions_pagination(request, selection)

            return jsonify({
                'success': True,
                'questions':  paginated_questions,
                'total_questions': len(selection),
                'current_category': None
            })
        except:
            abort(404)

        
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:categorie_id>/questions')
    def GetQuestionBycategorie(categorie_id):
        
        # all_questions = Question.query.order_by(Question.id).filter_by(category = categorie_id).all()
        # categorie = Category.query.get(categorie_id)
        # if len(all_questions) == 0:
        #     abort(404)
        # else:
        #     questions =questions_pagination(request,all_questions)
            
        #     return jsonify({
        #     "success": True,
        #     "questions": questions,
        #     "current_category": categorie.type,
        #     "total_questions": len(questions)
        # })
        category = Category.query.filter_by(id=categorie_id).one_or_none()
        if (category is None):
            abort(422)

        questions = Question.query.filter_by(category=categorie_id).all()

        # paginate questions
        paginated_questions = questions_pagination(request, questions,)

        # return the results
        return jsonify({
            'success': True,
            'questions': paginated_questions,
            'total_questions': len(questions),
            'current_category': category.type
        })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_games():
        previous_questions = request.get_json().get('previous_questions')
        quiz_category = request.get_json().get('quiz_category')
        if ((quiz_category is None) or (previous_questions is None)):
            abort(400)
        if (quiz_category['id'] == 0):
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=quiz_category['id']).all()
        def get_random_question():
            return questions[random.randint(0, len(questions)-1)]
        next_question = get_random_question()
        found = True
        while found:
            if next_question.id in previous_questions:
                next_question = get_random_question()
            else:
                found = False
        return jsonify({
            'success': True,
            'question': next_question.format(),
        }), 200
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
  
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
      }), 404

    @app.errorhandler(422)
    def unprocessable(error):
      return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable ressource"
      }), 422

    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
      }), 400

    @app.errorhandler(500)
    def server_error(error):
      return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal Server Error"
      })

    return app

