# Sử dụng Nginx nhẹ
FROM nginx:alpine

# Xóa file mặc định của Nginx
RUN rm -rf /usr/share/nginx/html/*

# COPY toàn bộ code trong thư mục hiện tại vào thư mục web của Nginx
COPY . /usr/share/nginx/html/

# Expose port 80
EXPOSE 80

# Chạy Nginx
CMD ["nginx", "-g", "daemon off;"]