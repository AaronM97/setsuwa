from flask_restful import Resource, reqparse 
from flask_backend.models import User, Blog
from flask_backend import db_api,db
from flask import jsonify, g
from flask_jwt_extended import jwt_required

parser = reqparse.RequestParser()
parser.add_argument('user_id')
parser.add_argument('post_id')
parser.add_argument('title')
parser.add_argument('content')
parser.add_argument('tag')
parser.add_argument('filter')

class User_Access(Resource):
    # @jwt_required -> commented out for development
    def get(self):
        data = parser.parse_args() 
        try:
            return_user = User.find_by_id(data['user_id'])
            g.user = return_user
            return jsonify(return_user.to_object()) # 200
        except:
            return {"message": "request failed"}, 500

class Post(Resource):
    # @jwt_required -> commented out for development
    def post(self):
        data = parser.parse_args()
        try:
            if data['user_id'] == str(g.user.user_id):
                new_blog = Blog(data['user_id'],data['title'],data['content'],data['tag'])
                new_blog.save_to_db()
                return {"message" :"Post created",
                        "post_id": new_blog.post_id},200
            else:
                return {"message": "Create post failed"}, 500
        except:
            db.session.close()
            return {"message": "Create post failed"}, 500

    def get(self):
        data = parser.parse_args() 
        try:
            return_blog = Blog.find_by_id(data['post_id'])
            return jsonify(return_blog.to_object())
        except:
            db.session.close()
            return {"message": "Retrieve post failed"}, 500

     # @jwt_required -> commented out for development & it is your post
    def delete(self):
        data = parser.parse_args()
        if(Blog.find_by_id(data['post_id'])):
            try:
                Blog.delete_by_id(data['post_id'])
                return {"message": "Post deleted"}, 200
            except:
                db.session.close()
                return {"message": "Delete post failed"}, 500
        return {"message": "Delete post failed"}, 400

    # @jwt_required -> commented out for development &  it is your post
    def put(self):
        data = parser.parse_args()
        try:
            Blog.edit_by_id(data['post_id'], data['title'], data['content'], data['tag'])
            return {"message" : "Post updated",
                    "post_id" : data['post_id']}, 200
        except:
            db.session.close()
            return {"message" : "Post update failed"}, 400
        
class Posts(Resource):
    def get(self):
        data = parser.parse_args()
        filter = "pop"
        try:
            if(data['filter']):
                filter = data['filter']
            if(data['user_id']):
                blogs = Blog.find_user_posts(data['user_id'],filter)
            elif(data['tag']):
                blogs = Blog.find_tag_posts(data['tag'],filter)
            else:
                blogs = Blog.find_posts(filter)

            blogs_objs = []
            for blog in blogs:
                blogs_objs.append(blog.to_object())
                
            if(blogs_objs) :
                return jsonify(blogs_objs)
            else:
                db.session.close()
                return {"message" : "No posts found"}, 400
        except:
            return {"message" : "No posts found"}, 500

db_api.add_resource(User_Access,"/db/user")
db_api.add_resource(Post,"/db/post")
db_api.add_resource(Posts,"/db/posts")