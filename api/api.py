from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api, Resource, reqparse
from variance import calculatePortfolioVariance

app = Flask(__name__)
cors = CORS(app)
api = Api(app)

variance_post_args = reqparse.RequestParser()
variance_post_args.add_argument("portfolio", type=dict, location="json", help="Portfolio is required in dictionary format", required=True)
variance_post_args.add_argument("period", type=str, choices=('1y', '2y', '5y'), default="1y", required=False)
variance_post_args.add_argument("interval", type=str, choices=('1h', '1d', '1wk', '1mo'),  default="1d", required=False)


class Variance(Resource):
    def post(self):
        print("Received POST request")
        args = variance_post_args.parse_args()
        variance, sd = calculatePortfolioVariance(args['portfolio'], args['period'], args['interval'])
        return {"variance": variance, "sd": sd}


api.add_resource(Variance, "/variance")

if __name__ == '__main__':
    app.run(debug=True)
