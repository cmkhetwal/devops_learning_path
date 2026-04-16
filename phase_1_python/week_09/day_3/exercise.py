"""
Week 9, Day 3: Docker Image Management

MANAGING DOCKER IMAGES WITH PYTHON
===================================

In this exercise you will build functions that work with Docker images
using mock objects.  These patterns transfer directly to the real Docker SDK.

TASKS
-----
1. Create a MockImage class
2. Build an image registry simulator
3. Write an image size analyzer
4. Create an image cleanup function
5. Generate an image inventory report
"""


# ============================================================
# TASK 1: Create a MockImage class
# ============================================================
# Create a class called `MockImage` with:
#   __init__(self, name, tag="latest", size_mb=100):
#       - self.name     = name
#       - self.tags     = [f"{name}:{tag}"]
#       - self.size_mb  = size_mb
#       - self.short_id = f"sha256:{abs(hash(name)) % 10**10:010d}"
#       - self.attrs    = {
#             "Size": size_mb * 1024 * 1024,
#             "Created": "2024-01-15T10:30:00Z",
#             "Os": "linux",
#             "Architecture": "amd64"
#         }
#
#   Methods:
#       tag(repository, tag="latest"):
#           - Appends f"{repository}:{tag}" to self.tags
#       __repr__():
#           - Returns "Image(<first tag>, <size_mb>MB)"

# YOUR CODE HERE


# ============================================================
# TASK 2: Image registry simulator
# ============================================================
# Create a class called `ImageRegistry` with:
#   __init__(self):
#       - self.images = []    (empty list)
#
#   Methods:
#       pull(name, tag="latest", size_mb=100):
#           - Creates a MockImage and appends to self.images
#           - Prints "Pulled <name>:<tag> (<size_mb>MB)"
#           - Returns the new image
#
#       list_images():
#           - Returns the full list of images
#
#       get_image(name_and_tag):
#           - name_and_tag is like "nginx:latest"
#           - Search through images; return the one that has name_and_tag
#             in its .tags list.  Return None if not found.
#
#       remove_image(name_and_tag):
#           - Find the image with name_and_tag in its .tags
#           - Remove it from self.images
#           - Print "Removed <name_and_tag>"
#           - Return True if found/removed, False otherwise
#
#       total_size_mb():
#           - Return the sum of .size_mb for all images

# YOUR CODE HERE


# ============================================================
# TASK 3: Image size analyzer
# ============================================================
# Write a function called `analyze_image_sizes` that:
#   - Takes one argument: images (list of MockImage)
#   - Returns a dictionary with:
#       "total_mb"      -> sum of all size_mb
#       "average_mb"    -> average size_mb (float, rounded to 1 decimal)
#       "largest"       -> the name of the largest image (first tag)
#       "smallest"      -> the name of the smallest image (first tag)
#       "count"         -> number of images
#   - Prints "Image Analysis: X images, total Y MB"
#     where X is count and Y is total_mb

# YOUR CODE HERE


# ============================================================
# TASK 4: Image cleanup function
# ============================================================
# Write a function called `cleanup_old_images` that:
#   - Takes two arguments: registry (ImageRegistry), keep_list (list of str)
#   - keep_list contains tag strings like ["nginx:latest", "python:3.11"]
#   - Removes any image from the registry whose FIRST TAG is NOT in keep_list
#   - Prints "Keeping: <tag>" for images kept
#   - Prints "Removing: <tag>" for images removed
#   - Returns the number of images removed

# YOUR CODE HERE


# ============================================================
# TASK 5: Image inventory report
# ============================================================
# Write a function called `image_inventory_report` that:
#   - Takes one argument: registry (ImageRegistry)
#   - Returns a multi-line string:
#
#     Docker Image Inventory
#     ======================
#     IMAGE                          SIZE        ID
#     <tag>                          <X> MB      <short_id>
#     ...
#     ----------------------
#     Total: X images, Y MB
#
#   Rules:
#     - IMAGE column: 30 chars wide, left-aligned (use first tag)
#     - SIZE column: size_mb right-aligned in 6 chars, followed by " MB"
#     - ID column: short_id
#     - Sort images alphabetically by first tag
#     - The dashes line is 22 dashes

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  WEEK 9, DAY 3 - Image Management")
    print("=" * 55)

    # Task 1 test
    print("\n--- Task 1: MockImage ---")
    img = MockImage("nginx", "latest", 150)
    print(repr(img))
    img.tag("myregistry.com/nginx", "v1.0")
    print(f"Tags: {img.tags}")

    # Task 2 test
    print("\n--- Task 2: ImageRegistry ---")
    registry = ImageRegistry()
    registry.pull("nginx", "latest", 150)
    registry.pull("python", "3.11", 350)
    registry.pull("redis", "7", 80)
    registry.pull("postgres", "15", 400)
    registry.pull("alpine", "3.18", 5)
    print(f"Total images: {len(registry.list_images())}")
    print(f"Total size: {registry.total_size_mb()} MB")
    found = registry.get_image("redis:7")
    print(f"Found redis: {repr(found)}")

    # Task 3 test
    print("\n--- Task 3: Size Analysis ---")
    analysis = analyze_image_sizes(registry.list_images())
    for k, v in analysis.items():
        print(f"  {k}: {v}")

    # Task 4 test
    print("\n--- Task 4: Cleanup ---")
    keep = ["nginx:latest", "python:3.11"]
    removed_count = cleanup_old_images(registry, keep)
    print(f"Removed {removed_count} images, {len(registry.list_images())} remaining")

    # Task 5 test - re-populate
    registry.pull("redis", "7", 80)
    registry.pull("node", "20", 300)
    print("\n--- Task 5: Inventory Report ---")
    report = image_inventory_report(registry)
    print(report)
