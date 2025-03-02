class Solution {
    public int trap(int[] A) {
      int preMax = 0;
      int postMax = 0;
      int[] prefixMax = new int[A.length];
      int[] postfixMax = new int[A.length];
      for(int i = 0; i < A.length; i++) {
          preMax = Math.max(preMax, A[i]);
          prefixMax[i] = preMax;
          postMax = Math.max(postMax, A[A.length - i - 1]);
          postfixMax[A.length - i - 1] = postMax;
      }
      int total = 0;
      for(int i = 0; i < A.length; i++) {
          total += Math.min(prefixMax[i], postfixMax[i]) - A[i];
      }
      return total;
    }
}
