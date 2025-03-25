from .base import MongoDB
from bson import ObjectId


class LocationDB(MongoDB):
    async def get_cities(self):
        return await self.db.cities.find({"is_active": True}).to_list(length=None)

    async def get_categories(self):
        return await self.db.categories.find({"is_active": True}).to_list(length=None)
    
    async def get_subcategories(self, category_id: str):
        return await self.db.subcategories.find(
            {"category": ObjectId(category_id), "is_active": True}
        ).to_list(length=None)

    async def get_locations_by_param(self, city_id: str, category_id: str, subcategory_id: str):
        return await self.db.locations.find(
            {
                "city": ObjectId(city_id),
                "category": ObjectId(category_id),
                "subcategory": ObjectId(subcategory_id),
                "is_active": True
            }
        ).to_list(length=None)
    
    async def get_location_by_id(self, location_id: str):
        """Get a specific location by ID"""
        return await self.db.locations.find_one({"_id": ObjectId(location_id)})
    
    async def get_comments_by_location(self, location_id: str):
        """Get comments from a location document"""
        location = await self.get_location_by_id(location_id)
        if location and "comments" in location:
            return location.get("comments", [])
        return []

    async def get_location_images(self, location_id: str):
        """Get all images for a specific location"""
        loc = await self.get_location_by_id(location_id)
        if not loc or not loc.get('images'):
            return []
        
        image_list = []
        for img_obj in loc.get('images', []):
            if 'image' in img_obj and img_obj['image']:
                image_list.append(str(img_obj['image']))
        
        return image_list

    async def get_image_file(self, file_id: str):
        """Get image file metadata by ID"""
        return await self.db.images.files.find_one({"_id": ObjectId(file_id)})

    async def get_image_data(self, file_id: str):
        """Get binary image data from chunks collection"""
        cursor = self.db.images.chunks.find({"files_id": ObjectId(file_id)}).sort("n", 1)
        
        if not cursor:
            return None
        
        data = bytearray()
        async for chunk in cursor:
            if chunk.get("data"):
                # Extract binary data from the chunk
                chunk_data = chunk.get("data")
                if isinstance(chunk_data, dict) and "$binary" in chunk_data:
                    # Handle MongoDB binary format
                    import base64
                    binary_data = base64.b64decode(chunk_data["$binary"]["base64"])
                    data.extend(binary_data)
                else:
                    # Handle regular binary data
                    data.extend(chunk_data)
        
        return bytes(data) if data else None

    async def add_comment(self, location_id: str, user_id: int, user_name: str, rating: int, comment_text: str):
        """Add a new comment to a location's comments array"""
        from datetime import datetime
        
        # Create comment document
        comment = {
            "user_id": str(user_id),
            "user_name": user_name,
            "text": comment_text,
            "rating": float(rating),
            "created_at": datetime.now()
        }
        
        # Add comment to the location's comments array
        result = await self.db.locations.update_one(
            {"_id": ObjectId(location_id)},
            {"$push": {"comments": comment}}
        )
        
        # Update location's average rating
        if result.modified_count > 0:
            # Get all comments for this location
            location = await self.get_location_by_id(location_id)
            
            if location and "comments" in location:
                comments = location.get("comments", [])
                total_rating = sum(comment.get("rating", 0) for comment in comments)
                count = len(comments)
                
                if count > 0:
                    avg_rating = total_rating / count
                    
                    # Update location with new average rating and count
                    await self.db.locations.update_one(
                        {"_id": ObjectId(location_id)},
                        {"$set": {"average_rating": avg_rating, "rating_count": count}}
                    )
                
                return True
        
        return False