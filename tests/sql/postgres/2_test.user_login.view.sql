-- 1. Create a view called user_login that contains the username and password columns from the user table.
CREATE OR REPLACE VIEW public.user_login AS
SELECT username, password
FROM public.user;
