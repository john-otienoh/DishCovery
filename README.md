# DishCovery your Personal Digital Cookbook

DishCovery is a user-friendly, full-featured recipe management app that helps food lovers explore, organize, and share their favorite recipes from around the world.

## 🔧 Core Features

- 🌍 Browse & search thousands of recipes by ingredients, cuisine, or category
- 📝 Add, edit, and delete your own recipes
- 📸 Upload images of your dishes
- 📦 Save ingredients to a shopping list
- 🧑‍🍳 Step-by-step cooking instructions
- 💾 User authentication and saved recipe collections

## 🌟 Objectives

- To make cooking accessible and fun for everyone — from beginners to seasoned chefs.
- Allow users to sign up, log in, and manage their accounts.
- Enable users to create and publish recipes with ingredients, instructions, and photos.
- Facilitate recipe search based on keywords, ingredients, cuisine types, and dietary preferences.
- Support social interactions such as rating, commenting, and sharing recipes.
- Provide notifications for user activity and recipe updates.

## Project Description

**Backend Description**
The "Recipe Sharing API" project aims to develop an API where users can share, search for, and interact with recipes. This API will enable users to create accounts, save their favorite recipes, and engage with the community by rating and commenting on recipes. By providing a platform for culinary enthusiasts to discover and exchange recipes, this API aims to foster a vibrant cooking community.

1. User Management

- Sign Up: Users can create an account by providing a username, email, and password.
- Login: Users can log in using their email and password.
- Profile Management: Users can update their profile information and preferences.

2. Recipe Management

- Create Recipes: Users can create and publish recipes with ingredients, instructions, and photos.
- Search Recipes: Users can search for recipes based on keywords, ingredients, cuisine types, and dietary preferences.
- Save Favorite Recipes: Users can save recipes to their profile for quick access.

3. Community Interaction

- Rate Recipes: Users can rate recipes on a scale and provide feedback.
- Comment on Recipes: Users can leave comments on recipes, ask questions, or share tips.
- Follow Users: Users can follow other users to stay updated on their recipes and activity.

4. Social Features

- Share Recipes: Users can share recipes with friends via email, social media, or direct messaging.
- Tagging and Categorization: Recipes can be tagged and categorized by cuisine type, meal type, and dietary restrictions.

5. Notifications

- Activity Notifications: Users receive notifications for likes, comments, and follows.
- Recipe Updates: Users can opt-in to receive updates on recipes they follow.

## Non-Functional Requirements

- Scalability: The API should handle a growing number of users, recipes, and interactions.
- Performance: The API should have a fast response time and handle concurrent requests efficiently.
- Security: Implement authentication and authorization mechanisms to protect user data.
- Reliability: The API should be highly available and handle failures gracefully.
- Usability: The API should be easy to use and well-documented.

## Use Cases

- User Sign Up and Login: New users sign up and existing users log in.
- Create and Publish Recipes: Users create and publish their own recipes.
- Search Recipes: Users search for recipes based on various criteria.
- Rate and Comment on Recipes: Users rate recipes and leave comments.
- Save Favorite Recipes: Users save recipes to their profile.
- Follow Other Users: Users follow other users to discover new recipes.

## Technical Requirements

- Programming Language: Python(Django and Drf).
- Database: Use a database to store user data, recipes, comments, and interactions (PostgreSQL&SQLite).
- Authentication: Implement JWT for secure user authentication.
- Search Functionality: Implement efficient search algorithms for recipe retrieval.
- API Documentation: Use Swagger or similar tools for API documentation.

## API Endpoints

1. User Management

```bash
POST /signup: Register a new user.
POST /login: Authenticate a user.
GET /profile: Get user profile details.
PUT /profile: Update user profile.
```

3. Recipe Management

```bash
POST /recipes: Create a new recipe.
GET /recipes/{id}: Get details of a specific recipe.
GET /recipes/search: Search for recipes based on criteria.
```

3. Interaction Features

```bash
POST /recipes/{id}/rate: Rate a recipe.
POST /recipes/{id}/comments: Comment on a recipe.
POST /recipes/{id}/save: Save a recipe to favorites.
POST /users/{user_id}/follow: Follow another user.
```

4. Social Features

```bash
POST /recipes/{id}/share: Share a recipe.
GET /users/{user_id}/recipes: Get recipes published by a user.
```

5. Notifications

```bash
GET /notifications: Get notifications for user activity.
```

## Security

Use HTTPS to encrypt data in transit.</hr>
Implement input validation and sanitization to prevent SQL injection and XSS attacks.</hr>
Use strong password hashing algorithms like bcrypt.

## Performance

Implement caching strategies to improve response times.</hr>
Optimize database queries to handle large datasets efficiently.</hr>
Use load balancing to distribute traffic evenly across servers.

## Documentation

Provide comprehensive API documentation using tools like Swagger.</hr>
Create user guides and developer documentation to assist with integration and usage
