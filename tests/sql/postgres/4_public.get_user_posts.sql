-- Function with parameters and RETURNS TABLE
CREATE OR REPLACE FUNCTION public.get_user_posts(user_name VARCHAR)
    RETURNS TABLE
            (
                post_title VARCHAR,
                post_date  TIMESTAMP
            )
AS
$$
BEGIN
    RETURN QUERY SELECT post_title,
                        created_at AS post_date
                 FROM public.posts
                 WHERE user_id = (SELECT user_id FROM public.users WHERE username = user_name);
END;
$$ LANGUAGE plpgsql;