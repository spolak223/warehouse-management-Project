# Welcome to my second project - Completed until Errors are found
> This project has been inspired by one of my previous jobs. I found it intriguing how the entire system works and wanted to implement it in myself, although I do not have a massive dataset, I was able to find a small CSV file to use.

# Current devlog
## 26/12/2025
> Officially finished the project! Added a stock control feature where you can order new stock, edit the status of orders and a better way to views orders / invoices.

# Project Features
> Fully working system for creating a user and also logging them in
> Database for storing hashed usernames and hashed passwords
> Different panels for admin users and normal users
> Normal users can only view stocks and search, as well as applying filters
> Admin users have a range of different options:
  > Appointing and removing admin privileges
  > Creating orders
  > Viewing Orders and Invoices, where invoices will only be created for "pending" or "completed" orders
  > Editing the status of orders to "pending" or "completed"
  > Stock control option where you can order more stock of a product
> 3 different databases for storing user information, order information and product information
> The orders databases has 3 tables which are linked: business -<- (One-to-Many) order -- (One-to-One) invoices

# Additional Information
> During the creation of the project around 95% of it was created on my own with the help of online resources along with trial and error; however, the remaining 5% was created with the help of AI, when I did not understand something at all, I would use it to explain something to me and teach me it, rather than giving me the direct solution.

