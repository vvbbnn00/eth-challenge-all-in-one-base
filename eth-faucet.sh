while (true) do
  # Faucet init
  eth-faucet -wallet.provider http://127.0.0.1:18545/ -wallet.privkey "${ALLOC_ADDRESS_PRIVATE_KEY}" -faucet.minutes 1
  echo "Unexpected eth-faucet exit, restarting in 5 seconds..."
  sleep 5
done
