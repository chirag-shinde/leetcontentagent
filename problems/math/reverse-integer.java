// LeetCode #7: Reverse Integer (Medium) - https://leetcode.com/problems/reverse-integer
package problems.math;

class Solution {
    public int reverse(int x) {
        try{
            int res = 0;
            int remainder = 0;
            boolean isNegative = x < 0 ? true : false;
            if(isNegative) {
                x *= -1;
            }
            while(x > 0){
                if(res > Integer.MAX_VALUE / 10) {
                    return  0;
                }
                res *= 10;
                remainder = x % 10;
                res += remainder;
                x = x/10;
            }

            return isNegative? res * -1: res;
        } catch(NumberFormatException n) {
            return 0;
        }
    }
}
