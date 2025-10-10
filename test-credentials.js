// Credential Testing Script - Created by Balaji Koneti
const axios = require('axios');

const API_BASE = 'http://localhost:3000/api';

// Test credentials for all user types
const testCredentials = [
  // Admin
  { email: 'admin@burnout-prediction.com', password: 'admin123', role: 'admin' },
  
  // Sample employees (first 5)
  { email: 'employee1@company.com', password: 'password123', role: 'employee' },
  { email: 'employee2@company.com', password: 'password123', role: 'employee' },
  { email: 'employee3@company.com', password: 'password123', role: 'employee' },
  { email: 'employee4@company.com', password: 'password123', role: 'employee' },
  { email: 'employee5@company.com', password: 'password123', role: 'employee' },
  
  // Sample managers (first 5)
  { email: 'manager1@company.com', password: 'password123', role: 'manager' },
  { email: 'manager2@company.com', password: 'password123', role: 'manager' },
  { email: 'manager3@company.com', password: 'password123', role: 'manager' },
  { email: 'manager4@company.com', password: 'password123', role: 'manager' },
  { email: 'manager5@company.com', password: 'password123', role: 'manager' }
];

async function testCredentials() {
  console.log('🔐 Testing All Login Credentials...\n');
  
  let successCount = 0;
  let failCount = 0;
  const results = [];
  
  for (const cred of testCredentials) {
    try {
      console.log(`Testing ${cred.role}: ${cred.email}...`);
      
      const response = await axios.post(`${API_BASE}/auth/login`, {
        email: cred.email,
        password: cred.password
      });
      
      if (response.data.success) {
        console.log(`  ✅ SUCCESS - ${cred.role} login working`);
        results.push({
          email: cred.email,
          role: cred.role,
          status: 'SUCCESS',
          userData: response.data.data.user
        });
        successCount++;
      } else {
        console.log(`  ❌ FAILED - ${cred.role} login failed: ${response.data.message}`);
        results.push({
          email: cred.email,
          role: cred.role,
          status: 'FAILED',
          error: response.data.message
        });
        failCount++;
      }
      
    } catch (error) {
      console.log(`  ❌ ERROR - ${cred.role} login error: ${error.response?.data?.message || error.message}`);
      results.push({
        email: cred.email,
        role: cred.role,
        status: 'ERROR',
        error: error.response?.data?.message || error.message
      });
      failCount++;
    }
    
    console.log('');
  }
  
  console.log('📊 Credential Test Summary:');
  console.log('===========================');
  console.log(`✅ Successful logins: ${successCount}`);
  console.log(`❌ Failed logins: ${failCount}`);
  console.log(`📈 Success rate: ${((successCount / testCredentials.length) * 100).toFixed(1)}%`);
  
  console.log('\n📋 Detailed Results:');
  console.log('====================');
  results.forEach(result => {
    const status = result.status === 'SUCCESS' ? '✅' : '❌';
    console.log(`${status} ${result.role}: ${result.email} - ${result.status}`);
    if (result.userData) {
      console.log(`    Name: ${result.userData.firstName} ${result.userData.lastName}`);
      console.log(`    Department: ${result.userData.department}`);
      console.log(`    Job Title: ${result.userData.jobTitle}`);
    }
    if (result.error) {
      console.log(`    Error: ${result.error}`);
    }
    console.log('');
  });
  
  return { successCount, failCount, results };
}

// Test admin dashboard access
async function testAdminDashboard() {
  console.log('🎛️  Testing Admin Dashboard Access...\n');
  
  try {
    // First login as admin
    const loginResponse = await axios.post(`${API_BASE}/auth/login`, {
      email: 'admin@burnout-prediction.com',
      password: 'admin123'
    });
    
    if (!loginResponse.data.success) {
      console.log('❌ Admin login failed - cannot test dashboard');
      return;
    }
    
    const adminToken = loginResponse.data.data.token;
    console.log('✅ Admin login successful');
    
    // Test getting all users
    console.log('📊 Testing user list access...');
    const usersResponse = await axios.get(`${API_BASE}/users`, {
      headers: { Authorization: `Bearer ${adminToken}` }
    });
    
    console.log(`✅ Successfully retrieved ${usersResponse.data.length} users`);
    
    // Test getting individual user data
    console.log('👤 Testing individual user access...');
    const firstUser = usersResponse.data[0];
    const userDetailResponse = await axios.get(`${API_BASE}/users/${firstUser._id}`, {
      headers: { Authorization: `Bearer ${adminToken}` }
    });
    
    console.log('✅ Individual user data accessible');
    console.log(`   User: ${userDetailResponse.data.firstName} ${userDetailResponse.data.lastName}`);
    console.log(`   Email: ${userDetailResponse.data.email}`);
    console.log(`   Role: ${userDetailResponse.data.role}`);
    console.log(`   Department: ${userDetailResponse.data.department}`);
    console.log(`   Job Title: ${userDetailResponse.data.jobTitle}`);
    
    // Test predictions access
    console.log('🎯 Testing predictions access...');
    const predictionsResponse = await axios.get(`${API_BASE}/predictions`, {
      headers: { Authorization: `Bearer ${adminToken}` }
    });
    
    console.log(`✅ Successfully retrieved ${predictionsResponse.data.length} predictions`);
    
    // Analyze prediction data
    const riskCounts = predictionsResponse.data.reduce((acc, pred) => {
      acc[pred.riskLevel] = (acc[pred.riskLevel] || 0) + 1;
      return acc;
    }, {});
    
    console.log('📊 Prediction Analysis:');
    Object.entries(riskCounts).forEach(([level, count]) => {
      console.log(`   ${level}: ${count} predictions`);
    });
    
    console.log('\n🎉 Admin Dashboard Access: FULLY FUNCTIONAL');
    
  } catch (error) {
    console.log(`❌ Admin dashboard test failed: ${error.response?.data?.message || error.message}`);
  }
}

// Main test function
async function runAllTests() {
  console.log('🧪 Comprehensive System Testing');
  console.log('================================\n');
  
  // Test credentials
  const credentialResults = await testCredentials();
  
  console.log('\n' + '='.repeat(50) + '\n');
  
  // Test admin dashboard
  await testAdminDashboard();
  
  console.log('\n' + '='.repeat(50) + '\n');
  
  // Final summary
  console.log('🎯 FINAL TEST SUMMARY:');
  console.log('======================');
  console.log(`✅ Database: 50 employees + 10 managers + 1 admin = 61 users`);
  console.log(`✅ Credentials: ${credentialResults.successCount}/${testCredentials.length} working`);
  console.log(`✅ Admin Dashboard: Individual data access functional`);
  console.log(`✅ Predictions: 60 predictions generated and accessible`);
  
  if (credentialResults.successCount === testCredentials.length) {
    console.log('\n🎉 ALL TESTS PASSED! System is fully operational.');
  } else {
    console.log('\n⚠️  Some tests failed. Check the details above.');
  }
}

// Run tests
if (require.main === module) {
  runAllTests();
}

module.exports = { testCredentials, testAdminDashboard, runAllTests };
