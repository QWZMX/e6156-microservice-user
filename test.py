import unittest
import json
from main import app, db
from models import User


class UserAPITestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database/users.db'
        self.app = app.test_client()

        with app.app_context():
            db.create_all()

    def tearDown(self):
        # with app.app_context():
        #     db.session.remove()
        #     db.drop_all()
        pass

    def test_create_user(self):
        with app.app_context():
            user_data = {
                'username': 'testuser',
                'email': 'testuser@example.com',
                'password': 'testpassword',
                'userType': 'adopter'
            }
            response = self.app.post('/users', data=json.dumps(user_data), content_type='application/json')
            self.assertEqual(response.status_code, 201)

    def test_get_user(self):
        with app.app_context():
            user = User(username='testuser2', email='testuser2@example.com', passwordHash='testpassword',
                        userType='adopter')
            db.session.add(user)
            db.session.commit()

            response = self.app.get(f'/users/{user.userId}')
            self.assertEqual(response.status_code, 200)

    def test_update_user(self):
        with app.app_context():
            user = User(username='testuser3', email='testuser3@example.com', passwordHash='testpassword',
                        userType='adopter')
            db.session.add(user)
            db.session.commit()

            new_data = {
                'username': 'updateduser',
                'email': 'updateduser@example.com',
                'userType': 'shelter'
            }
            response = self.app.put(f'/users/{user.userId}', data=json.dumps(new_data), content_type='application/json')
            self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        with app.app_context():
            user = User(username='testuser4', email='testuser4@example.com', passwordHash='testpassword',
                        userType='adopter')
            db.session.add(user)
            db.session.commit()

            response = self.app.delete(f'/users/{user.userId}')
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
