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
