# Welcome to my second project - Still Under Development
> This project has been inspired by one of my previous jobs. I found it intriguing how the entire system works and wanted to implement it in myself, although I do not have a massive dataset, I was able to find a small CSV file to use.

# Current devlog
## 10/11/2025
> Ran into my first real roadblocks
1. Originally tried to store cursor in the init function, however this led to record locking and I wasn't able to manage any of the admins. This has now been fixed
2. The logged in user can actually remove themselves as an admin. This then kicks them off the admin homepage and they aren't able to become admins again
3. When a users role is changed to an admin, they don't always have admin rights for some reason, need to fix this.
