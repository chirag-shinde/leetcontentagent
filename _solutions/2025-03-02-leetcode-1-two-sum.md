---
title: "LeetCode 1: Two Sum"
date: 2025-03-02 22:43:00
slug: two-sum
problem_number: 1
difficulty: Easy
leetcode_url: https://leetcode.com/problems/two-sum/
problem_statement: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice."
approach: "Use a hash map to store previously seen numbers and their indices. For each number, check if its complement (target - current number) exists in the hash map."
code: "class Solution:\n    def twoSum(self, nums, target):\n        \"\"\"\n        Find the indices of two numbers that add up to the target.\n        \n        Args:\n            nums: List of integers\n            target: Integer target sum\n            \n        Returns:\n            List of two indices\n        \"\"\"\n        # Using a hash map for O(n) time complexity\n        num_map = {}\n        \n        for i, num in enumerate(nums):\n            complement = target - num\n            if complement in num_map:\n                return [num_map[complement], i]\n            num_map[num] = i\n            \n        return []  # No solution found"
language: python
time_complexity: "O(n)"
space_complexity: "O(n)"
tags:
  - Python
  - Hash Table
  - Array
layout: solution
---

This solution to the Two Sum problem uses a hash map (dictionary in Python) to achieve an efficient one-pass solution.

The key insight is that we can use a hash map to remember numbers we've seen previously and their indices. This allows us to quickly check if the complement of the current number (target - current number) has already been seen.

Here's how the algorithm works:

1. We initialize an empty hash map `num_map` to store numbers and their indices.
2. We iterate through the `nums` array:
   - For each number, we calculate its complement: `complement = target - num`
   - If the complement is already in the hash map, we've found our solution
   - Otherwise, we add the current number and its index to the hash map

When we find a match, we return an array containing the index of the complement (stored in the hash map) and the current index.

This algorithm is efficient with:
- Time complexity of O(n) - we only need one pass through the array
- Space complexity of O(n) - in the worst case, we might need to store almost all elements in the hash map

This is significantly better than the brute force approach of checking all pairs of numbers, which would take O(n²) time.
