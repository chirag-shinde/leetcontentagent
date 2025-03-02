# LeetCode Solution Blog

An automated blog that creates detailed explanations for LeetCode problem solutions. When you push a solution (Python, Java, or Go) to this repository, a GitHub Action automatically:

1. Analyzes your solution code
2. Generates a detailed explanation using OpenAI
3. Creates a blog post with problem explanation, approach, code walkthrough, and complexity analysis
4. Publishes the updated blog to GitHub Pages

## How It Works

### Adding a New LeetCode Solution

1. Create a file with your LeetCode solution in Python, Java, or Go
2. Include a comment at the top in this format (language-specific comment style):
   
   For Python:
   ```python
   # LeetCode #123: Two Sum (Easy) - https://leetcode.com/problems/two-sum/
   ```
   
   For Java:
   ```java
   // LeetCode #123: Two Sum (Easy) - https://leetcode.com/problems/two-sum/
   ```
   
   For Go:
   ```go
   // LeetCode #123: Two Sum (Easy) - https://leetcode.com/problems/two-sum/
   ```

3. Push the file to the repository
4. The GitHub Action will automatically process the solution and update the blog

### Example Solution Formats

#### Python
```python
# LeetCode #1: Two Sum (Easy) - https://leetcode.com/problems/two-sum/

class Solution:
    def twoSum(self, nums, target):
        """
        Find the indices of two numbers that add up to the target.
        
        Args:
            nums: List of integers
            target: Integer target sum
            
        Returns:
            List of two indices
        """
        # Using a hash map for O(n) time complexity
        num_map = {}
        
        for i, num in enumerate(nums):
            complement = target - num
            if complement in num_map:
                return [num_map[complement], i]
            num_map[num] = i
            
        return []  # No solution found
```

#### Java
```java
// LeetCode #1: Two Sum (Easy) - https://leetcode.com/problems/two-sum/

class Solution {
    /**
     * Find the indices of two numbers that add up to the target.
     *
     * @param nums Array of integers
     * @param target Target sum
     * @return Array of two indices
     */
    public int[] twoSum(int[] nums, int target) {
        // Using a hash map for O(n) time complexity
        Map<Integer, Integer> numMap = new HashMap<>();
        
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (numMap.containsKey(complement)) {
                return new int[] {numMap.get(complement), i};
            }
            numMap.put(nums[i], i);
        }
        
        return new int[] {}; // No solution found
    }
}
```

#### Go
```go
// LeetCode #1: Two Sum (Easy) - https://leetcode.com/problems/two-sum/

func twoSum(nums []int, target int) []int {
    // Using a hash map for O(n) time complexity
    numMap := make(map[int]int)
    
    for i, num := range nums {
        complement := target - num
        if idx, found := numMap[complement]; found {
            return []int{idx, i}
        }
        numMap[num] = i
    }
    
    return []int{} // No solution found
}
```

## Setup Instructions

### Prerequisites

- GitHub account
- OpenAI API key (for generating explanations)

### Configuration

1. Clone this repository
2. Add your OpenAI API key as a GitHub secret named `OPENAI_API_KEY`
3. Push a LeetCode solution in the format described above
4. Wait for GitHub Actions to build and deploy the site
5. Your blog will be available at: `https://[your-username].github.io/leetcontentagent/`

## Customization

You can customize the blog by:

- Editing `_config.yml` to change site settings
- Modifying the Jekyll templates in `_layouts` and `_includes` directories
- Updating CSS in `assets/css` directory

## Local Development

To run the blog locally:

1. Install Ruby and Jekyll
2. Run `bundle install` to install dependencies
3. Run `bundle exec jekyll serve` to start the local server
4. Visit `http://localhost:4000/leetcontentagent/` in your browser

## License

MIT
