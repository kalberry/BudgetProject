import os
import markdown

from budget_api.models import User, Bill, Database
from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)
db = models.Database()

app.config['SECRET_KEY'] = 'applesauce'
db.create_tables()

@app.route("/api/v1")
def index():
    with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
        content = markdown_file.read()

        return markdown.markdown(content)

class User(Resource):
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id')
        args = parser.parse_args()

        if (args['id']):
            user = db.get_users(id=args['id'])
            if (user != []):
                return {"message": "User retrieved", "data": user}, 200
            else:
                return {"message": "User not found"}, 404
        else:
            users = db.get_users()
            if (users != []):
                return {"message": "Retrieved all users.", "data": users}, 200
            else:
                return {"message": "Count not find user"}, 404

    def put(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)
        parser.add_argument('email')
        parser.add_argument('password_hash')
        parser.add_argument('last_pay_date')
        parser.add_argument('pay_frequency')
        parser.add_argument('pay_dates', action='append')

        args = parser.parse_args()

        message = 'For ' + str(args['id']) + " we "
        if (args['email']):
            db.update_user(id=args['id'], email=args['email'])
            message += 'updated email. '
        if (args['password_hash']):
            db.update_user(id=args['id'], password_hash=args['password_hash'])
            message += 'updated password. '
        if (args['last_pay_date']):
            db.update_user(id=args['id'], last_pay_date=args['last_pay_date'])
            message += 'updated starting pay date. '
        if (args['pay_frequency']):
            db.update_user(id=args['id'], pay_frequency=args['pay_frequency'])
            message += 'updated pay frequency. '
        if (args['pay_dates']):
            db.update_user(id=args['id'], pay_dates=args['pay_dates'])
            message += 'updated pay dates. '

        user = db.get_users(id=args['id'])
        if (user):
            return {"message": message}, 200
        else:
            return {"message": "Failed to update user"}, 404

    def delete(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)

        args = parser.parse_args()

        db.delete_user(args['id'])

        return 204

class Bill(Resource):
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('user_id')
        parser.add_argument('id', action='append')
        parser.add_argument('category')

        args = parser.parse_args()

        # TODO: Maybe user id and bill id?
        if (args['user_id'] and args['id']):
            return {"message": "Bad Request"}, 400
        elif (args['user_id'] and not args['id']):
            bills = db.get_bills(user_id=args['user_id'])
            if bills != []:
                return {"message": "Received bills successfully", "data": bills}, 200
            else:
                return {"message": "Cannot find bills"}, 404
        elif (not args['user_id'] and args['id']):
            if len(args['id']) > 1:
                bills = []
                for i in args['id']:
                    bills.append(db.get_bills(id=i)[0])
                if bills != []:
                    return {"message": "Received bill successfully", "data": bills}, 200
                else:
                    return {"message": "Cannot find bills"}, 404
            else:
                bill = db.get_bills(id=args['id'][0])
                if bill != []:
                    return {"message": "Received bill successfully", "data": bill}, 200
                else:
                    return {"message", "Cannot find bill"}, 404

        bills = db.get_bills()
        if bills != []:
            return {"message": "Getting all bills", "data": bills}, 200
        else:
            return {"message", "Cannot find bills"}, 404

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('user_id', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('cost', required=True)
        parser.add_argument('due_date')
        parser.add_argument('frequency')
        parser.add_argument('last_paid', required=True)
        parser.add_argument('category')

        args = parser.parse_args()

        if args['frequency'] and not args['due_date']:
            b = models.Bill(user_id=args['user_id'], name=args['name'], cost=args['cost'], due_date=args['due_date'], frequency=None, last_paid=args['last_paid'], category=args['category'])

            db.add_bill(b)
            return {"message": args['name'] + " bill with the cost of $" + args['cost']}, 201
        elif not args['frequency'] and args['due_date']:
            b = models.Bill(user_id=args['user_id'], name=args['name'], cost=args['cost'], due_date=args['due_date'], frequency=None, last_paid=args['last_paid'], category=args['category'])

            db.add_bill(b)
            return {"message": args['name'] + " bill with the cost of $" + args['cost']}, 201

        return {"message": "Bad Request"}, 400

    def delete(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)

        args = parser.parse_args()

        db.delete_bill(args['id'])

        return {"message": "Bill deleted."}, 204

    def put(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)
        parser.add_argument('name')
        parser.add_argument('cost')
        parser.add_argument('category')

        args = parser.parse_args()

        id = args['id']
        name = args['name']
        cost = args['cost']
        category = args['category']

        if name:
            db.update_bill(id=id, name=name)
        if cost:
            db.update_bill(id=id, cost=cost)
        if category:
            db.update_bill(id=id, category=category)

        bill = db.get_bills(id=id)

        if bill != []:
            return {"message": "Bill updated.", "data": bill}, 200
        else:
            return {"message": "Bill not found."}, 404

class PayPeriodExpense(Resource):
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('user_id')
        parser.add_argument('id', action='append')
        parser.add_argument('category')

        args = parser.parse_args()

        if (args['user_id'] and args['id']):
            return {"message": "Bad Request"}, 400
        elif (args['user_id'] and not args['id']):
            ppe = db.get_pay_period_expenses(user_id=args['user_id'])
            if ppe != []:
                return {"message": "Received pay period expenses successfully", "data": ppe}, 200
            else:
                return {"message": "Cannot find pay period expenses"}, 404
        elif (not args['user_id'] and args['id']):
            if len(args['id']) > 1:
                ppe = []
                for i in args['id']:
                    ppe.append(db.get_pay_period_expenses(id=i)[0])
                if ppe != []:
                    return {"message": "Received pay period expenses successfully", "data": ppe}, 200
                else:
                    return {"message": "Cannot find pay period expenses"}, 404
            else:
                ppe = db.get_pay_period_expenses(id=args['id'][0])
                if ppe != []:
                    return {"message": "Received pay period expense successfully", "data": ppe}, 200
                else:
                    return {"message": "Cannot find pay period expenses"}, 404

        ppe=db.get_pay_period_expenses()
        if ppe != []:
            return {"message": "Getting all bills", "data": db.get_bills()}, 200
        else:
            return {"message": "Cannot find pay period expenses"}, 404

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('user_id', required=True)
        parser.add_argument('name', required=True)
        parser.add_argument('cost', required=True)
        parser.add_argument('category')

        args = parser.parse_args()

        db.add_pay_period_expense(name=args['name'], cost=args['cost'], user_id=args['user_id'], category=args['category'])

        return {"message": "Pay period expense added successfully"}, 201

    def delete(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)

        args = parser.parse_args()

        db.delete_pay_period_expense(args['id'])

        return 204

    def put(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)
        parser.add_argument('name')
        parser.add_argument('cost')
        parser.add_argument('category')

        args = parser.parse_args()

        id = args['id']
        name = args['name']
        cost = args['cost']
        category = args['category']

        if name:
            db.update_pay_period_expense(id=id, name=name)
        if cost:
            db.update_pay_period_expense(id=id, cost=cost)
        if category:
            db.update_pay_period_expense(id=id, category=category)

        ppe = db.get_pay_period_expenses(id=id)

        if ppe != []:
            return {"message": "Pay period updated.", "data": ppe}, 200
        else :
            return {"message": "Cannot retrieve pay period expense."}, 404

class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('email', required=True)
        parser.add_argument('password_hash', required=True)
        parser.add_argument('last_pay_date', required=True)
        parser.add_argument('pay_frequency')
        parser.add_argument('pay_dates', action='append')

        args = parser.parse_args()

        email = args['email']
        password_hash = args['password_hash']
        last_pay_date = args['last_pay_date']
        pay_frequency = args['pay_frequency']
        pay_dates = args['pay_dates']

        user = db.register_user(email, password_hash, last_pay_date, pay_frequency, pay_dates)

        if user != {}:
            return {"message": "User registered", "data": user}, 201
        else:
            return{"message": "User failed to register"}, 404

class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('email', required=True)
        parser.add_argument('password', required=True)

        args = parser.parse_args()

        user = db.login_user(args['email'], args['password'])

        if user != []:
            return {"message": "User logged in", "data": user}, 200
        else:
            return{"message": "User failed to login"}, 404

class BudgetSchedule(Resource):
    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('id', required=True)
        parser.add_argument('count')

        args = parser.parse_args()
        id = args['id']
        count = args['count']

        if count == None:
            count = 24

        budget_schedule =  db.get_budget_schedule(user_id=id, count=count)
        if (budget_schedule != []):
            return {"message": "Budget Schedule recieved", "data": budget_schedule}, 200
        else:
            return {"message": "Budget Schedule not recieved"}, 404

api.add_resource(User, '/api/v1/users')
api.add_resource(Bill, '/api/v1/bills')
api.add_resource(PayPeriodExpense, '/api/v1/ppe')
api.add_resource(Register, '/api/v1/auth/register')
api.add_resource(Login, '/api/v1/auth/login')
api.add_resource(BudgetSchedule, '/api/v1/budget-schedule')
