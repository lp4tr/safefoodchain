/*
Data Layer - Smart Contract (Hyperledger Fabric Chaincode)

Chaincode che gestisce la logica di business per la tracciabilità prodotti alimentari.
Implementa il Data Layer garantendo immutabilità e auditabilità delle transazioni.
*/

package main

import (
	"encoding/json"
	"fmt"
	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// FoodAsset rappresenta un prodotto alimentare nella filiera.
type FoodAsset struct {
	AssetID      string  `json:"assetId"`
	ProductType  string  `json:"productType"`
	Quantity     float64 `json:"quantity"`
	Unit         string  `json:"unit"`
	Origin       string  `json:"origin"`
	CurrentStage string  `json:"currentStage"`
	Owner        string  `json:"owner"`
}

// FoodContract definisce il contratto intelligente.
type FoodContract struct {
	contractapi.Contract
}

// CreateAsset registra un nuovo prodotto alimentare sulla blockchain.
//
// RBAC: Verifica semplificata a livello chaincode tramite parametro userRole.
// Solo utenti con ruolo "producer" possono creare asset.
func (c *FoodContract) CreateAsset(ctx contractapi.TransactionContextInterface, assetID string, productType string, quantity float64, unit string, origin string, userRole string) error {
	// RBAC semplificato: verifica ruolo tramite parametro
	// Nota: integrazione completa con MSP/identity layer demandata ad altri livelli
	if userRole != "producer" {
		return fmt.Errorf("Access Denied: only producers can create assets")
	}

	exists, err := c.AssetExists(ctx, assetID)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("asset %s already exists", assetID)
	}

	clientID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return err
	}

	asset := FoodAsset{
		AssetID:      assetID,
		ProductType:  productType,
		Quantity:     quantity,
		Unit:         unit,
		Origin:       origin,
		CurrentStage: "Raccolto",
		Owner:        clientID,
	}

	bytes, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(assetID, bytes)
}

// DeleteAsset elimina un asset dal ledger.
//
// RBAC: Solo producer può eliminare asset.
func (c *FoodContract) DeleteAsset(ctx contractapi.TransactionContextInterface, assetID string, userRole string) error {
	// RBAC semplificato: verifica ruolo tramite parametro
	if userRole != "producer" {
		return fmt.Errorf("Access Denied: only producers can delete assets")
	}

	exists, err := c.AssetExists(ctx, assetID)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("the asset %s does not exist", assetID)
	}

	return ctx.GetStub().DelState(assetID)
}

// UpdateStage aggiorna lo stadio del prodotto nella filiera.
//
// RBAC: Solo producer e logistics possono aggiornare lo stadio.
// Immutabilità: Ogni aggiornamento viene registrato come transazione separata nel Ledger.
func (c *FoodContract) UpdateStage(ctx contractapi.TransactionContextInterface, assetID string, newStage string, userRole string) error {
	// RBAC semplificato: verifica ruolo tramite parametro
	if userRole != "producer" && userRole != "logistics" {
		return fmt.Errorf("Access Denied")
	}

	asset, err := c.ReadAsset(ctx, assetID)
	if err != nil {
		return err
	}

	clientID, err := ctx.GetClientIdentity().GetID()
	if err != nil {
		return err
	}

	asset.CurrentStage = newStage
	asset.Owner = clientID

	bytes, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(assetID, bytes)
}

// ReadAsset recupera le informazioni di un asset dal ledger.
//
// Query di sola lettura: non modifica lo stato, non richiede consenso.
func (c *FoodContract) ReadAsset(ctx contractapi.TransactionContextInterface, assetID string) (*FoodAsset, error) {
	bytes, err := ctx.GetStub().GetState(assetID)
	if err != nil {
		return nil, err
	}
	if bytes == nil {
		return nil, fmt.Errorf("asset %s not found", assetID)
	}

	var asset FoodAsset
	if err := json.Unmarshal(bytes, &asset); err != nil {
		return nil, err
	}

	return &asset, nil
}

// AssetExists verifica se un asset esiste nel ledger.
//
// Utilizzata internamente da CreateAsset per garantire integrità dati.
func (c *FoodContract) AssetExists(ctx contractapi.TransactionContextInterface, assetID string) (bool, error) {
	bytes, err := ctx.GetStub().GetState(assetID)
	if err != nil {
		return false, err
	}
	return bytes != nil, nil
}

// main inizializza e avvia il chaincode sulla rete Fabric.
func main() {
	chaincode, err := contractapi.NewChaincode(new(FoodContract))
	if err != nil {
		panic(err)
	}
	if err := chaincode.Start(); err != nil {
		panic(err)
	}
}