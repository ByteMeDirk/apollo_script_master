-- Stored Procedure with OUT parameters
CREATE OR REPLACE PROCEDURE public.insert_user(
    in_username VARCHAR,
    in_email VARCHAR,
    OUT out_user_id INT,
    OUT out_created_at TIMESTAMP
)
AS
$$
BEGIN
    INSERT INTO public.users (username, email)
    VALUES (in_username, in_email)
    RETURNING user_id, created_at INTO out_user_id, out_created_at;
END;
$$ LANGUAGE plpgsql;