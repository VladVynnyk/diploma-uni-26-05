1. Create payments via fondy
2. Create reflection/image of payed order in dashboards of consultant and customer - Added
3. Create table for skills of consultant in card (should be below description)
4. Create mobile view of dashboard (fix view of section with buttons) - Fixed by usage of button in the bottom of screen
5. Create orders section in dashboard (here should be orders and as consultant and as customer(just marked with different tags)) - Created a sample version or single order component

6. In footer make less options. (Or adapt this options to my business)
7. Make filters in main page different a little bit. +
8. Make design of chat a little better.
9. Make design of accordeon button a little better. (Not important)
10. Also, needed to review color scheme of website.


11. Add "averageScore" field to database table "User"
12. Add reviews to users/ endpoint - Added
13. Add another endpoint "users/consultants/", which should return only users with is_consultant=True - Instead I updated endpoint users/.
14. Fix database layer, when updating consultants. Tags, reviews should be the same. +-
15. Add features for update user in dashboard. +
16. Add button "Dashboard" to header, when user is logged in. +
16.1 Update should work and for regular users, and for consultants. +

17. Add Restrictions to password in form +
18. Create handling of expired tokens
19. Create deleting tags in input +
20. Make choosing tags from dropdown
21. Add col "rating" to "User" model. And make auto counting of rating, when reviews are added.
22. Add validation of tags. Case
23. Fix adding duplicate tags in different users. 
24. Add viewing reviews
25. Add feature for adding reviews, in dashboard for consultant.

26. Fix caching responses with reviews in endpoints /users/paginated, /users/offset.
27. Make selecting last 5 reviews of consultant.
