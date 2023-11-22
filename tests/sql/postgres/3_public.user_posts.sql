DROP VIEW  IF EXISTS public.user_posts CASCADE;
CREATE VIEW public.user_posts AS
SELECT users.username,
       posts.post_title
FROM public.users
         JOIN
     public.posts ON users.user_id = posts.user_id;