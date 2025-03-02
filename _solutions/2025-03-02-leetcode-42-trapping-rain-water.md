---
title: "LeetCode 42: Trapping Rain Water"
date: 2025-03-02 22:41:00
slug: trapping-rain-water
problem_number: 42
difficulty: Hard
leetcode_url: https://leetcode.com/problems/trapping-rain-water/
problem_statement: "Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining."
approach: "Use prefix and postfix max arrays to determine the water level at each position."
code: "class Solution {\n    public int trap(int[] A) {\n      int preMax = 0;\n      int postMax = 0;\n      int[] prefixMax = new int[A.length];\n      int[] postfixMax = new int[A.length];\n      for(int i = 0; i < A.length; i++) {\n          preMax = Math.max(preMax, A[i]);\n          prefixMax[i] = preMax;\n          postMax = Math.max(postMax, A[A.length - i - 1]);\n          postfixMax[A.length - i - 1] = postMax;\n      }\n      int total = 0;\n      for(int i = 0; i < A.length; i++) {\n          total += Math.min(prefixMax[i], postfixMax[i]) - A[i];\n      }\n      return total;\n    }\n}"
language: java
time_complexity: "O(n)"
space_complexity: "O(n)"
tags:
  - Java
  - Array
  - Two Pointers
  - Dynamic Programming
layout: solution
---

This solution to the Trapping Rain Water problem uses an efficient approach with prefix and postfix maximum arrays.

The key insight is that the amount of water that can be trapped at any position `i` depends on the minimum of the maximum heights to the left and right of that position, minus the height at the current position.

Here's how the algorithm works:

1. We create two arrays:
   - `prefixMax`: Stores the maximum height seen so far from the left
   - `postfixMax`: Stores the maximum height seen so far from the right

2. We calculate these arrays in a single pass through the input array:
   - For `prefixMax`, we iterate from left to right
   - For `postfixMax`, we iterate from right to left (simultaneously in one loop)

3. Then we calculate the trapped water at each position:
   - At each position `i`, the water trapped is `min(prefixMax[i], postfixMax[i]) - A[i]`
   - If this value is negative, it means no water is trapped at that position (when the current bar is the highest)

The time complexity is O(n) as we only need two passes through the array.
The space complexity is also O(n) for storing the prefix and postfix maximum arrays.

An alternative approach could use two pointers to achieve the same result with O(1) space complexity, but this solution is more straightforward to understand.
