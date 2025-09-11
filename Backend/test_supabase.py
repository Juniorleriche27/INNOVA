from supabase import create_client

url = "https://hbdvgoqctgmlxthrdkiq.supabase.co"  # URL du projet
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhiZHZnb3FjdGdtbHh0aHJka2lxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQyNjc5MzksImV4cCI6MjA2OTg0MzkzOX0.ORtkjq3wG6cx-8QyVSQgOo7YIWzsbGXJcZg5fTHVAKk"
supabase = create_client(url, key)

response = supabase.table("contributors").select("*").execute()
print(response.data)
