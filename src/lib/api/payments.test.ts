import {afterEach,expect,it,vi} from 'vitest';
import {createPaymentIntent,retryCashfreePayment,verifyCashfreePayment,verifyMockPayment,type PaymentIntent} from './payments';
afterEach(()=>vi.unstubAllGlobals());
const intent:PaymentIntent={paymentId:1,orderId:2,orderNumber:'test-order',provider:'mock',providerOrderId:'mock_order_1',amount:20,amountPaise:2000,currency:'INR'};
it('never sends mock verification for a real or unknown provider',async()=>{
 const request=vi.fn();vi.stubGlobal('fetch',request);
 for(const provider of ['razorpay','unknown','']) await expect(verifyMockPayment({...intent,provider},'test')).rejects.toThrow('secure gateway checkout');
 expect(request).not.toHaveBeenCalled();
});
it('retains explicit mock-provider simulation and surfaces verification failure',async()=>{
 const request=vi.fn().mockResolvedValueOnce({ok:true}).mockResolvedValueOnce({ok:false,status:400});vi.stubGlobal('fetch',request);
 await verifyMockPayment(intent,'Mock QA');
 expect(JSON.parse(request.mock.calls[0][1].body)).toMatchObject({paymentId:1,providerOrderId:'mock_order_1'});
 await expect(verifyMockPayment(intent,'Mock QA')).rejects.toThrow('verification failed');
});

it('rejects malformed Cashfree return identifiers before making a request',async()=>{
 const request=vi.fn();vi.stubGlobal('fetch',request);
 await expect(verifyCashfreePayment(0,'cf-order')).rejects.toThrow('details are invalid');
 await expect(verifyCashfreePayment(2_147_483_648,'cf-order')).rejects.toThrow('details are invalid');
 await expect(verifyCashfreePayment(5,'')).rejects.toThrow('details are invalid');
 await expect(verifyCashfreePayment(5,'x'.repeat(129))).rejects.toThrow('details are invalid');
 expect(request).not.toHaveBeenCalled();
});

it('asks the backend to verify the returned payment instead of trusting browser status',async()=>{
 const payment={id:5,orderId:9,orderNumber:'SLC-TEST-9',provider:'cashfree',providerOrderId:'cf-order-9',amount:600,amountPaise:60000,currency:'INR',status:'SUCCESS'};
 const request=vi.fn().mockResolvedValue({ok:true,json:async()=>payment});vi.stubGlobal('fetch',request);
 await expect(verifyCashfreePayment(5,'cf-order-9')).resolves.toEqual(payment);
 expect(request).toHaveBeenCalledOnce();
 expect(JSON.parse(request.mock.calls[0][1].body)).toEqual({paymentId:5,providerOrderId:'cf-order-9'});
});

it('sends the guest order capability in the payment intent body, never the URL',async()=>{
 const intent={...intentBase(),provider:'cashfree',environment:'sandbox'};
 const request=vi.fn().mockResolvedValue({ok:true,json:async()=>intent});vi.stubGlobal('fetch',request);
 await createPaymentIntent('CB-20261031-AB12','guest-capability');
 expect(request.mock.calls[0][0]).toContain('/payments/intent');
 expect(request.mock.calls[0][0]).not.toContain('guest-capability');
 expect(JSON.parse(request.mock.calls[0][1].body)).toEqual({orderNumber:'CB-20261031-AB12',guestOrderToken:'guest-capability'});
});

it('retries the referenced payment with the guest capability in a JSON body',async()=>{
 const request=vi.fn().mockResolvedValue({ok:true,json:async()=>({...intent,paymentId:2})});vi.stubGlobal('fetch',request);
 await retryCashfreePayment(1,'guest-capability');
 expect(request.mock.calls[0][0]).toContain('/payments/1/retry');
 expect(request.mock.calls[0][0]).not.toContain('guest-capability');
 expect(request.mock.calls[0][1]).toMatchObject({method:'POST'});
 expect(JSON.parse(request.mock.calls[0][1].body)).toEqual({guestOrderToken:'guest-capability'});
});

it('parses backend FAILED/PENDING details returned with HTTP 400 for safe retry decisions',async()=>{
 const payment={id:5,orderId:9,orderNumber:'CB-20261031-AB12',provider:'cashfree',providerOrderId:'cf-order-9',amount:898,amountPaise:89800,currency:'INR',status:'FAILED',verificationState:'FAILED',canRetry:true,detail:'not paid'};
 const request=vi.fn().mockResolvedValue({ok:false,status:400,json:async()=>payment});vi.stubGlobal('fetch',request);
 await expect(verifyCashfreePayment(5,'cf-order-9')).resolves.toMatchObject({status:'FAILED',verificationState:'FAILED',canRetry:true});
});

function intentBase(): PaymentIntent { return {paymentId:1,orderId:2,orderNumber:'CB-20261031-AB12',provider:'mock',providerOrderId:'mock_order_1',amount:898,amountPaise:89800,currency:'INR'}; }
